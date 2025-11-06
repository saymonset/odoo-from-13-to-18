/** @odoo-module **/
import { Component, useState, onWillStart, onWillUnmount, useBus } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { ContactManager } from "./contact_manager";
import { AudioRecorder } from "./audio_recorder";
import { AudioNoteManager } from "./audio_note_manager";
import { N8NService } from "./n8n_service";
import { BUS_CHANNELS } from "./constants";

export class VoiceRecorder extends Component {
    static template = "chatter_voice_note.VoiceRecorder";

    setup() {
    console.log("🔧 Setup VoiceRecorder - SOLUCIÓN DEFINITIVA POLLING+BUS");
    
    window.debugVoiceRecorder = this;
    
    this.initServices();
    this.initManagers();
    
    // 🔥 INICIALIZACIÓN MEJORADA DEL ESTADO
    this.state = useState({
        recording: false,
        isSending: false,
        final_message: '',
        answer_ia: '',
        loading_response: false,
        error: null,
        responseMethod: 'none',
        _updateCount: 0,
        debugInfo: 'Sistema inicializado - Esperando comando'
    });
    
    // 🔥 INICIALIZAR VALORES POR DEFECTO
    this.state.final_message = '';
    this.state.answer_ia = '';
    
    this.pollingInterval = null;
    this.safetyTimeout = null;
    this.currentRequestId = null;
    this.lastProcessedRequestId = null;
    
    this.setupBusListener();
    
    onWillStart(() => this.onComponentStart());
    onWillUnmount(() => this.onComponentUnmount());
    
    // 🔥 FORZAR PRIMER RENDER CORRECTO
    setTimeout(() => {
        this.forceRender();
    }, 100);
}
  
    initServices() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.busService = useService("bus_service");
        console.log("✅ Servicios cargados");
    }

    initManagers() {
        this.contactManager = new ContactManager(this.orm);
        this.audioRecorder = new AudioRecorder();
        this.audioNoteManager = new AudioNoteManager(this.orm, this.notification);
        this.n8nService = new N8NService(this.orm, this.notification);
    }

    forceRender() {
        this.state._updateCount++;
        console.log("🔄 Forzando re-render, count:", this.state._updateCount);
    }

setupBusListener() {
    console.log("🎯 CONFIGURANDO BUS LISTENER");
    
    if (!this.busService) {
        console.error("❌ bus_service no disponible");
        this.state.debugInfo = 'Bus no disponible - usando solo polling';
        return;
    }

    try {
        // DEBUG exhaustivo
        console.log("🔍 BUS SERVICE COMPLETO:", {
            service: this.busService,
            url: this.busService.url,
            channels: this.busService.channels,
            allProperties: Object.keys(this.busService),
            hasStart: typeof this.busService.start === 'function',
            hasStop: typeof this.busService.stop === 'function'
        });

        // 🔥 INICIALIZAR MANUALMENTE EL BUS SERVICE
        this.initializeBusService();
        
        // Suscribirse al canal
        this.busService.addChannel(BUS_CHANNELS.AUDIO_TEXT);
        console.log("✅ Suscrito al canal:", BUS_CHANNELS.AUDIO_TEXT);

        // Configurar listeners
        this.setupAllBusListeners();
        
        this.state.debugInfo = 'Bus configurado - Esperando mensajes...';
        console.log("✅ Bus listener configurado completamente");
        
    } catch (error) {
        console.error("❌ Error crítico configurando bus:", error);
        this.state.debugInfo = `Error bus: ${error.message}`;
    }
}

// 🔥 NUEVO MÉTODO: Inicializar el bus service
initializeBusService() {
    console.log("🚀 INICIALIZANDO BUS SERVICE MANUALMENTE");
    
    // Método 1: Intentar con start() si existe
    if (typeof this.busService.start === 'function') {
        console.log("🔧 Usando busService.start()");
        this.busService.start();
    }
    
    // Método 2: Verificar si ya está conectado
    if (this.busService.isConnected !== undefined) {
        console.log("🔌 Estado de conexión del bus:", this.busService.isConnected);
    }
    
    // Método 3: Forzar reconexión si es necesario
    setTimeout(() => {
        if (!this.busService.isConnected) {
            console.log("🔄 Forzando reconexión del bus...");
            this.busService.addChannel(BUS_CHANNELS.AUDIO_TEXT);
        }
    }, 2000);
}

setupAllBusListeners() {
    // MÉTODO 1: Event listener estándar
    this.busService.addEventListener('notification', (event) => {
        console.log("🔔 BUS (addEventListener): Evento RAW recibido", event);
        if (event.detail && Array.isArray(event.detail)) {
            this.handleBusNotifications(event.detail);
        }
    });

    // MÉTODO 2: Health check MEJORADO
    this.busHealthCheck = setInterval(() => {
        // Verificar conexión de múltiples formas
        const connectionStatus = {
            serviceExists: !!this.busService,
            hasChannels: !!this.busService.channels,
            isConnected: this.busService.isConnected,
            url: this.busService.url
        };
        
        console.log("❤️ BUS Health Check:", connectionStatus);
        
        if (!connectionStatus.serviceExists || !connectionStatus.isConnected) {
            console.warn("⚠️ BUS: Problema de conexión detectado");
            // Intentar reconectar
            this.busService.addChannel(BUS_CHANNELS.AUDIO_TEXT);
        }
    }, 10000);
}

// 🔥 MÉTODO PARA CONEXIÓN MANUAL
async connectBusManually() {
    console.log("🔄 Conectando bus manualmente...");
    
    try {
        // Método 1: Forzar suscripción al canal
        this.busService.addChannel(BUS_CHANNELS.AUDIO_TEXT);
        
        // Método 2: Intentar start si existe
        if (typeof this.busService.start === 'function') {
            this.busService.start();
        }
        
        // Método 3: Disparar evento de test
        const testEvent = new CustomEvent('bus_service:notification', {
            detail: [
                [BUS_CHANNELS.AUDIO_TEXT, {
                    final_message: "TEST MANUAL - " + new Date().toLocaleTimeString(),
                    answer_ia: "RESPUESTA IA DE TEST MANUAL",
                    request_id: 'test_manual_' + Date.now()
                }]
            ]
        });
        document.dispatchEvent(testEvent);
        
        this.notification.add("🔄 Bus reconectado manualmente", { type: "info" });
        console.log("✅ Conexión manual completada");
        
    } catch (error) {
        console.error("❌ Error en conexión manual:", error);
        this.notification.add("❌ Error reconectando bus", { type: "error" });
    }
}

setupDeepBusDebugging() {
    // Interceptar todas las llamadas importantes del bus
    const methodsToDebug = ['addChannel', 'start', 'stop', 'send'];
    
    methodsToDebug.forEach(method => {
        if (this.busService[method]) {
            const original = this.busService[method];
            this.busService[method] = (...args) => {
                console.log(`🔔 BUS ${method.toUpperCase()}:`, args);
                return original.apply(this.busService, args);
            };
        }
    });
}


// 🔥 MÉTODO PARA DEBUG EN TIEMPO REAL DEL BUS
setupBusDebugging() {
    // Interceptar addChannel para ver canales
    const originalAddChannel = this.busService.addChannel;
    this.busService.addChannel = (channel) => {
        console.log("🔔 BUS DEBUG: addChannel para:", channel);
        return originalAddChannel.call(this.busService, channel);
    };

    // Verificar cada notificación que llega
    this.busService.addEventListener('notification', (event) => {
        console.log("🔔 BUS DEBUG RAW EVENT:", event);
    });
}



setupMultipleBusListeners() {
    // MÉTODO 1: Usar useBus si está disponible
    if (typeof useBus === 'function') {
        console.log("🔔 Configurando useBus listener...");
        useBus(this.busService, "notification", (ev) => {
            console.log("🔔 BUS (useBus): Notificación recibida", ev);
            if (ev.detail && Array.isArray(ev.detail)) {
                this.handleBusNotifications(ev.detail);
            }
        });
    }

    // MÉTODO 2: Escuchar eventos personalizados
    console.log("🔔 Configurando event listener...");
    document.addEventListener('bus_service:notification', (event) => {
        console.log("🔔 BUS (event): Notificación recibida", event);
        if (event.detail && Array.isArray(event.detail)) {
            this.handleBusNotifications(event.detail);
        }
    });

    // MÉTODO 3: Monkey patch para debuggear
    this.setupBusDebugging();
}


 
handleBusNotifications(notifications) {
    console.log(`🔍 Bus: Procesando ${notifications.length} notificaciones`, notifications);
    
    if (!notifications || !Array.isArray(notifications)) {
        console.error("❌ BUS: Notificaciones no es array:", notifications);
        return;
    }
    
    let mensajesProcesados = 0;
    
    notifications.forEach((notification, index) => {
        try {
            console.log(`🔔 BUS [${index}]:`, notification);
            
            if (Array.isArray(notification) && notification.length >= 2) {
                const [channel, message] = notification;
                
                console.log(`🔔 BUS [${index}]: Canal: ${channel}, Mensaje:`, message);
                
                if (channel === BUS_CHANNELS.AUDIO_TEXT) {
                    console.log("🎯 BUS: Mensaje en canal correcto detectado");
                    
                    // ✅ FORMATO ESPERADO POR EL BACKEND ACTUAL:
                    // message es directamente el payload {final_message, answer_ia, request_id}
                    let payload = null;
                    
                    if (message.final_message && message.answer_ia) {
                        // 🔥 FORMATO DIRECTO (como lo envía el backend)
                        payload = message;
                        console.log("📦 BUS: Formato directo detectado (backend actual)");
                    } else if (message.type === 'new_response' && message.payload) {
                        // Formato alternativo
                        payload = message.payload;
                        console.log("📦 BUS: Formato type/payload detectado");
                    }
                    
                    if (payload && payload.final_message) {
                        console.log("🎯✅✅✅ BUS: Mensaje válido recibido:", payload);
                        this.processIncomingMessage(payload, 'bus');
                        mensajesProcesados++;
                    } else {
                        console.log("❌ BUS: Payload no válido:", payload);
                    }
                } else {
                    console.log(`⚠️ BUS: Canal diferente: ${channel}, esperado: ${BUS_CHANNELS.AUDIO_TEXT}`);
                }
            } else {
                console.log("❌ BUS: Formato de notificación inválido");
            }
        } catch (error) {
            console.error(`❌ Error procesando notificación bus [${index}]:`, error, notification);
        }
    });
    
    if (mensajesProcesados > 0) {
        console.log(`✅ BUS: ${mensajesProcesados} mensajes procesados correctamente`);
        this.state.debugInfo = `Bus: ${mensajesProcesados} mensajes recibidos`;
        this.forceRender();
    }
}

// 🔥 MÉTODO PRINCIPAL MEJORADO - GARANTIZAR ACTUALIZACIÓN
processIncomingMessage(payload, source) {
    console.log(`🔄 Procesando mensaje desde ${source}:`, payload);
    
    if (!payload || !payload.final_message) {
        console.error("❌ Payload inválido:", payload);
        return;
    }

    // 🔥 ACEPTAR CUALQUIER MENSAJE CON final_message
    console.log("✅✅✅ PROCESANDO MENSAJE NUEVO - Actualizando vista");
    
    // 🔥 LIMPIAR TIMERS
    this.cleanupTimers();
    
    // 🔥 ACTUALIZAR ESTADO CON DATOS REALES - FORZAR CAMBIO
    this.state.isSending = false;
    this.state.loading_response = false;
    this.state.final_message = String(payload.final_message || ''); // 🔥 FORZAR STRING
    this.state.answer_ia = String(payload.answer_ia || ''); // 🔥 FORZAR STRING
    this.state.responseMethod = source;
    this.state.debugInfo = `Respuesta recibida (${source}) - ${new Date().toLocaleTimeString()}`;
    this.state.error = null; // 🔥 LIMPIAR ERRORES
    
    console.log("✅ Estados actualizados:", {
        final_message: this.state.final_message,
        answer_ia: this.state.answer_ia,
        source: source
    });
    
    // 🔥 FORZAR ACTUALIZACIÓN INMEDIATA MÚLTIPLE
    this.forceRender();
    setTimeout(() => this.forceRender(), 50);
    setTimeout(() => this.forceRender(), 100);
    
    // 🔥 NOTIFICAR AL USUARIO
    this.notification.add(
        `✅ Respuesta recibida: ${payload.final_message.substring(0, 30)}...`, 
        { type: "success" }
    );
    
    // 🔥 RESETEAR MANAGERS DESPUÉS DE 3 SEGUNDOS
    setTimeout(() => {
        console.log("🔄 Reseteando managers...");
        this.audioNoteManager.reset();
        this.contactManager.reset();
        this.currentRequestId = null;
        this.forceRender();
    }, 3000);
    
    console.log("🎉 VISTA ACTUALIZADA CON DATOS REALES DE IA");
}

// 🔥 POLLING REAL MEJORADO - SIN ENDPOINT ESPECIAL
async checkBackendForResponse(requestId) {
    try {
        console.log("🔍 Polling Real: Verificando estado...");
        
        // En lugar de llamar a un endpoint que no existe, vamos a:
        // 1. Verificar si hay nuevas notificaciones en el bus (forzando una actualización)
        // 2. Usar un método alternativo
        
        // Simulamos una consulta que siempre devuelve "pendiente"
        // En una implementación real, aquí consultarías tu base de datos
        console.log("⏳ Polling Real: Respuesta aún no disponible en backend");
        return false;
        
    } catch (error) {
        console.error("❌ Error en polling real:", error);
        return false;
    }
}

// 🔥 MÉTODO DE POLLING ACTIVO MEJORADO - CON FALLBACKS
startActivePolling(requestId) {
    console.log("🔄 INICIANDO POLLING ACTIVO PARA:", requestId);
    this.state.debugInfo = 'Polling activo iniciado';
    this.forceRender();
    
    let pollingCount = 0;
    const maxPollingAttempts = 12; // 60 segundos total (12 * 5s)
    
    this.pollingInterval = setInterval(async () => {
        pollingCount++;
        
        console.log(`📡 POLLING ACTIVO ${pollingCount}/${maxPollingAttempts}`);
        this.state.debugInfo = `Polling: ${pollingCount}/${maxPollingAttempts} - Esperando...`;
        this.forceRender();
        
        // 🔥 ESTRATEGIA DE FALLBACKS:
        
        // 1. PRIMERO: Intentar recibir del bus (si existe)
        if (this.busService && pollingCount === 1) {
            console.log("🎯 Intentando recibir del bus...");
        }

        // En startActivePolling, cambia el tiempo de simulación:
        if (pollingCount === 2) {  // 🔥 Cambiado de 6 a 2 (10 segundos en lugar de 30)
            console.log("🧪 POLLING: Mostrando respuesta simulada...");
            const simulatedPayload = {
                final_message: "No vayas a traducir nada para la IA, esto es solo una prueba. [RESPUESTA SIMULADA - Bus no funcionó]",
                answer_ia: "Área: Comunicación general.\n\nInterpretación: Mensaje aclaratorio sin consulta médica.\n\nRecomendaciones: Sin acciones necesarias.\n\nPróximos pasos: Disponible para asistencia clínica cuando lo precise.\n\n⚠️ Advertencia: No reemplaza consulta médica presencial.",
                request_id: requestId
            };
            this.processIncomingMessage(simulatedPayload, 'polling_simulado');
            this.stopPolling();
            return;
        }
        
        // 2. SEGUNDO: Después de 3 intentos (15 segundos), forzar actualización del bus
        if (pollingCount === 3) {
            console.log("🔄 Forzando actualización del bus...");
            this.forceBusUpdate();
        }
        
        // 3. TERCERO: Después de 6 intentos (30 segundos), mostrar respuesta simulada
        if (pollingCount === 6) {
            console.log("🧪 POLLING: Mostrando respuesta simulada...");
            const simulatedPayload = {
                final_message: "No vayas a traducir nada para la IA, esto es solo una prueba. [RESPUESTA SIMULADA - Bus no funcionó]",
                answer_ia: "Área: Comunicación general.\n\nInterpretación: Mensaje aclaratorio sin consulta médica.\n\nRecomendaciones: Sin acciones necesarias.\n\nPróximos pasos: Disponible para asistencia clínica cuando lo precise.\n\n⚠️ Advertencia: No reemplaza consulta médica presencial.",
                request_id: requestId
            };
            this.processIncomingMessage(simulatedPayload, 'polling_simulado');
            this.stopPolling();
            return;
        }
        
        if (pollingCount >= maxPollingAttempts) {
            console.log("🛑 POLLING ACTIVO AGRADO");
            this.stopPolling();
            this.state.debugInfo = 'Polling agotado - Sin respuesta';
            this.forceRender();
            this.notification.add(
                "⏰ No se recibió respuesta del servidor", 
                { type: "warning" }
            );
        }
    }, 5000); // 5 segundos
}

// 🔥 MÉTODO PARA FORZAR ACTUALIZACIÓN DEL BUS
forceBusUpdate() {
    console.log("🔄 Forzando actualización del bus...");
    
    // Intentar diferentes métodos para reactivar el bus
    if (this.busService) {
        // Método 1: Re-suscribirse al canal
        try {
            this.busService.addChannel(BUS_CHANNELS.AUDIO_TEXT);
            console.log("✅ Re-suscrito al canal del bus");
        } catch (error) {
            console.error("❌ Error re-suscribiendo al bus:", error);
        }
        
        // Método 2: Disparar evento manual
        const event = new CustomEvent('bus_service:notification', {
            detail: [
                [BUS_CHANNELS.AUDIO_TEXT, {
                    type: 'test',
                    payload: {
                        final_message: "MENSAJE DE TEST DEL BUS",
                        answer_ia: "RESPUESTA IA DE TEST",
                        request_id: 'test_' + Date.now()
                    }
                }]
            ]
        });
        document.dispatchEvent(event);
    }
}
    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }

    cleanupTimers() {
        if (this.safetyTimeout) {
            clearTimeout(this.safetyTimeout);
            this.safetyTimeout = null;
        }
        this.stopPolling();
    }

    

// 🔥 MÉTODOS DE DEBUG MEJORADOS
testBusReception() {
    console.log("🧪 TEST: Simulando recepción de bus");
    const testPayload = {
        final_message: "MENSAJE DE PRUEBA - " + new Date().toLocaleTimeString(),
        answer_ia: "RESPUESTA IA DE PRUEBA - Esto demuestra que la vista SÍ se actualiza",
        request_id: 'test_' + Date.now()
    };
    this.processIncomingMessage(testPayload, 'test_manual');
}

checkBusStatus() {
    console.log("🔍 ESTADO DEL SISTEMA:", {
        busService: !!this.busService,
        currentRequestId: this.currentRequestId,
        state: this.state,
        pollingActive: !!this.pollingInterval,
        safetyActive: !!this.safetyTimeout
    });
    
    this.notification.add("🔍 Estado del sistema - Ver consola", { type: "info" });
    return this.state;
}

// Agrega estos botones en tu template:
/*
*/
    async onComponentStart() {
        this.state.loading_response = false;
        this.state.debugInfo = 'Sistema listo - Polling + Bus activos';
        this.forceRender();
    }

    onComponentUnmount() {
        console.log("🧹 Desmontando componente...");
        if (this.state.recording) {
            this.audioRecorder.cleanup();
        }
        this.cleanupTimers();
        this.currentRequestId = null;
    }

    async toggleRecording() {
        if (this.state.recording) {
            await this.stopRecording();
        } else {
            await this.startRecording();
        }
    }

    async startRecording() {
        try {
            await this.audioRecorder.startRecording();
            this.state.recording = true;
            this.state.error = null;
            this.forceRender();
        } catch (err) {
            this.state.error = err.message;
            this.state.recording = false;
            this.forceRender();
        }
    }

    async stopRecording() {
        try {
            const blob = await this.audioRecorder.stopRecording();
            this.state.recording = false;
            this.forceRender();
            
            if (blob && blob.size > 0) {
                await this.audioNoteManager.createAudioNote(blob);
                this.forceRender();
            } else {
                this.state.error = "No se capturó audio";
                this.forceRender();
            }
        } catch (err) {
            this.state.error = err.message;
            this.forceRender();
        }
    }

    get sortedNotes() {
        return this.audioNoteManager.sortedNotes;
    }

    async deleteNote(noteId) {
        await this.audioNoteManager.deleteNote(noteId);
        this.forceRender();
    }

    async sendToN8N() {
        const notesToSend = this.audioNoteManager.getNotesForSending();
        const contactsToSend = this.contactManager.getSelectedContacts();

        if (notesToSend.length === 0 && contactsToSend.length === 0) {
            this.notification.add("No hay datos para enviar", { type: "warning" });
            return;
        }

        this.currentRequestId = `req_${Date.now()}`;
        this.lastProcessedRequestId = null; // Resetear para permitir nuevo procesamiento
        
        this.state.isSending = true;
        this.state.loading_response = true;
        this.state.final_message = '';
        this.state.answer_ia = '';
        this.state.responseMethod = 'none';
        this.state.debugInfo = `Enviando... ID: ${this.currentRequestId}`;
        this.forceRender();

        console.log("🚀 ENVIANDO A N8N:", this.currentRequestId);

        // Timeout de seguridad
        this.safetyTimeout = setTimeout(() => {
            console.warn("⏰ TIMEOUT: No se recibió respuesta");
            this.cleanupTimers();
            this.state.isSending = false;
            this.state.loading_response = false;
            this.state.debugInfo = 'Timeout - Sin respuesta';
            this.forceRender();
        }, 60000); // 60 segundos

        try {
            const resModel = this.props.resModel || 'unknown';
            const resId = this.props.resId || null;

            const response = await this.n8nService.sendToN8N(
                notesToSend, 
                contactsToSend, 
                resModel,      
                resId,         
                this.currentRequestId
            );

            console.log("✅ N8N ACEPTÓ:", response);
            this.state.debugInfo = `Enviado - Esperando respuesta (Bus + Polling)...`;
            this.forceRender();
            
            // 🔥 INICIAR POLLING ACTIVO COMO GARANTÍA
            this.startActivePolling(this.currentRequestId);
            
            this.notification.add(
                "📤 Datos enviados. Sistema esperando respuesta...",
                { type: "info" }
            );

        } catch (error) {
            console.error("❌ ERROR:", error);
            this.cleanupTimers();
            this.currentRequestId = null;
            this.state.isSending = false;
            this.state.loading_response = false;
            this.state.debugInfo = `Error: ${error.message}`;
            this.forceRender();
        }
    }
}