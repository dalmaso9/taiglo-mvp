-- Script para adicionar o campo photos à tabela experiences
-- Execute este script se a tabela já existir e não tiver o campo photos

-- Adicionar coluna photos se não existir
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'experiences' 
        AND column_name = 'photos'
    ) THEN
        ALTER TABLE experiences ADD COLUMN photos JSONB DEFAULT '[]';
    END IF;
END $$;

-- Verificar se a coluna foi adicionada
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'experiences' 
AND column_name = 'photos';
