-- SQL*Plus / SQLcl conectado COMO ADMINISTRADOR ao serviço FREEPDB1.
-- Exemplo: sqlplus system@localhost:1521/FREEPDB1 @oracle_preparar_usuario.sql
-- A senha será solicitada sem eco. Use laboratório novo; não modifica usuário existente.
WHENEVER SQLERROR EXIT SQL.SQLCODE
SET VERIFY OFF
ACCEPT senha CHAR PROMPT 'Senha do novo usuário DG_ACADEMY: ' HIDE
-- Não inclua aspas duplas na senha: elas delimitam o identificador no comando.
CREATE USER dg_academy IDENTIFIED BY "&senha" DEFAULT TABLESPACE users QUOTA 100M ON users;
UNDEFINE senha
GRANT CREATE SESSION, CREATE TABLE TO dg_academy;
-- CREATE INDEX em tabela própria não exige CREATE ANY INDEX.
SELECT comp_id,version,status FROM dba_registry WHERE comp_id='SDO';
PROMPT Conecte como DG_ACADEMY a FREEPDB1 e execute oracle_schema.sql.
