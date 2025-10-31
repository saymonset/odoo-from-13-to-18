psql -U odoo -d dbcliente1_18
DELETE FROM ir_module_module WHERE name = 'chatter_voice_note';
DELETE FROM ir_model_data WHERE name = 'module_chatter_voice_note' 
AND module = 'base' 
AND id NOT IN (
    SELECT MIN(id) 
    FROM ir_model_data 
    WHERE name = 'module_chatter_voice_note' 
    AND module = 'base'
);
SELECT id, module, name, model, res_id 
FROM ir_model_data 
WHERE name = 'module_chatter_voice_note' AND module = 'base';
 id | module |           name            |      model       | res_id 
----+--------+---------------------------+------------------+--------
 25778 | base   | module_chatter_voice_note | ir.module.module |     672
(1 row)


 DELETE FROM ir_module_module WHERE name = 'chatter_voice_note';

 DELETE FROM ir_asset WHERE name LIKE '%chatter_voice_note%';
DELETE FROM ir_attachment WHERE name LIKE '%chatter_voice_note%';
-- 1. Primero identifica el registro exacto
SELECT id, module, name, model, res_id 
FROM ir_model_data 
WHERE name = 'module_chatter_voice_note' AND module = 'base';

-- 2. Elimina el registro conflictivo (usa el ID que aparece en el resultado anterior)
DELETE FROM ir_model_data 
WHERE id = 25832;  -- <-- Cambia 68 por el ID que te aparezca

-- 3. Confirma los cambios
COMMIT;

-- 4. Verifica que se eliminó
SELECT id, module, name, model, res_id 
FROM ir_model_data 
WHERE name = 'module_chatter_voice_note' AND module = 'base';