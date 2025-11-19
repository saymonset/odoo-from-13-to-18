import requests
from bs4 import BeautifulSoup
import re
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_tasa_bcv_verified():
    """
    Versión mejorada que verifica múltiples patrones y valida la tasa
    """
    try:
        url = 'https://www.bcv.org.ve'
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        print("🔍 Conectando al BCV...")
        session = requests.Session()
        response = session.get(url, headers=headers, verify=False, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Estrategia 1: Buscar por el patrón específico del BCV actual
        print("📊 Buscando tasas en la página...")
        
        # Buscar todos los números que parezcan tasas de cambio
        all_text = soup.get_text()
        tasas_encontradas = re.findall(r'\b\d{1,3}(?:\.\d{3})*,\d{2,4}\b', all_text)
        
        print(f"🔢 Números encontrados que podrían ser tasas: {tasas_encontradas}")
        
        # Filtrar tasas plausibles (rango realista para el bolívar)
        tasas_plausibles = []
        for tasa in tasas_encontradas:
            # Convertir a número para validar
            try:
                valor = float(tasa.replace('.', '').replace(',', '.'))
                # Rango realista: entre 30 y 100,000 Bs por dólar
                if 30 <= valor <= 100000:
                    tasas_plausibles.append((tasa, valor))
            except ValueError:
                continue
        
        print(f"💰 Tasas plausibles encontradas: {tasas_plausibles}")
        
        # Estrategia 2: Buscar específicamente alrededor de "USD" o "Dólar"
        tasas_usd = []
        patrones_usd = [
            r'USD[\s\S]{0,50}?(\d{1,3}(?:\.\d{3})*,\d{2,4})',
            r'Dólar[\s\S]{0,50}?(\d{1,3}(?:\.\d{3})*,\d{2,4})',
            r'(\d{1,3}(?:\.\d{3})*,\d{2,4})[\s\S]{0,50}?USD',
            r'(\d{1,3}(?:\.\d{3})*,\d{2,4})[\s\S]{0,50}?Dólar'
        ]
        
        for patron in patrones_usd:
            matches = re.findall(patron, all_text, re.IGNORECASE)
            tasas_usd.extend(matches)
        
        print(f"💵 Tasas encontradas cerca de USD/Dólar: {list(set(tasas_usd))}")
        
        # Estrategia 3: Buscar elementos específicos por clase o ID
        elementos_clave = []
        
        # Buscar elementos que comúnmente contienen la tasa
        selectores = [
            'div', 'span', 'strong', 'td',
            '[class*="dolar"]', '[id*="dolar"]',
            '[class*="currency"]', '[class*="exchange"]',
            '.col-sm-6', '.pull-right', '.text-right'
        ]
        
        for selector in selectores:
            try:
                elementos = soup.select(selector)
                for elem in elementos[:20]:  # Limitar para no ser demasiado extenso
                    texto = elem.get_text(strip=True)
                    if re.search(r'\d{1,3}(?:\.\d{3})*,\d{2,4}', texto) and len(texto) < 100:
                        elementos_clave.append(texto)
            except:
                pass
        
        print("🏷️ Elementos HTML que contienen números:")
        for elem in elementos_clave[:10]:  # Mostrar solo los primeros 10
            print(f"   - {elem}")
        
        # Determinar la tasa más probable
        tasa_final = None
        
        # Prioridad 1: Tasas que aparecen cerca de USD
        if tasas_usd:
            tasa_final = tasas_usd[0]
            print(f"✅ Usando tasa encontrada cerca de USD: {tasa_final}")
        
        # Prioridad 2: La tasa más común entre las plausibles
        elif tasas_plausibles:
            # Contar frecuencia
            from collections import Counter
            tasas_count = Counter([t[0] for t in tasas_plausibles])
            tasa_comun = tasas_count.most_common(1)[0][0]
            tasa_final = tasa_comun
            print(f"✅ Usando tasa más común: {tasa_final}")
        
        # Prioridad 3: La primera tasa plausible
        elif tasas_plausibles:
            tasa_final = tasas_plausibles[0][0]
            print(f"✅ Usando primera tasa plausible: {tasa_final}")
        
        if tasa_final:
            # Validación final
            valor_numerico = float(tasa_final.replace('.', '').replace(',', '.'))
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"\n🎯 RESULTADO FINAL:")
            print(f"   Tasa BCV: Bs. {tasa_final}")
            print(f"   Valor numérico: {valor_numerico}")
            print(f"   Fecha de consulta: {fecha_actual}")
            
            return tasa_final, valor_numerico
        else:
            print("❌ No se pudo determinar una tasa válida")
            return None, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def verificar_tasa_con_fuente_externa():
    """
    Verifica contra una fuente alternativa para comparar
    """
    try:
        # Fuente alternativa: Dólar Today (mercado paralelo, solo para referencia)
        url_dt = "https://s3.amazonaws.com/dolartoday/data.json"
        response = requests.get(url_dt, timeout=10)
        if response.status_code == 200:
            data = response.json()
            usd_paralelo = data.get('USD', {}).get('promedio', 'N/A')
            usd_bcv = data.get('USD', {}).get('bcv', 'N/A')
            print(f"\n🔍 Referencia externa (DólarToday):")
            print(f"   BCV reportado: {usd_bcv}")
            print(f"   Paralelo: {usd_paralelo}")
    except:
        print("⚠️  No se pudo verificar con fuente externa")

if __name__ == "__main__":
    print("🚀 Iniciando verificación de tasa BCV...")
    tasa_str, tasa_num = get_tasa_bcv_verified()
    
    if tasa_str:
        print(f"\n💎 TASA OFICIAL BCV: Bs. {tasa_str} por USD")
        verificar_tasa_con_fuente_externa()
        
        print("\n📝 NOTA: Si la tasa no coincide con la oficial, puede ser porque:")
        print("   - El BCV actualiza la tasa en horarios específicos")
        print("   - Hay caché en el servidor del BCV")
        print("   - La estructura de la página cambió")
    else:
        print("\n❌ No se pudo obtener la tasa del BCV")