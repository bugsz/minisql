
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'AND CHAR COLUMN_OR_TABLE COMMA COMPARATOR CREATE DELETE DROP END EXECFILE FLOAT FROM INDEX INSERT INT INTO KEY LPAREN ON PK PRIMARY QUIT RPAREN SELECT STAR TABLE UNIQUE VALUES WHEREexpression : exp_drop\n                  | exp_select\n                  | exp_delete\n                  | exp_create\n                  | exp_insert\n                  | exp_quit\n                  | exp_execfileexp_create : CREATE TABLE COLUMN_OR_TABLE LPAREN exp_create_columns RPAREN END\n                  | CREATE INDEX COLUMN_OR_TABLE ON COLUMN_OR_TABLE LPAREN COLUMN_OR_TABLE RPAREN ENDexp_create_columns : exp_create_valid_column\n                          | exp_create_valid_column COMMA exp_create_columnsexp_create_valid_column : exp_create_valid_char\n                               | exp_create_valid_int\n                               | exp_create_valid_float\n                               | exp_create_valid_pkexp_create_valid_pk : PRIMARY KEY LPAREN exp_pk RPARENexp_pk : COLUMN_OR_TABLE\n              | COLUMN_OR_TABLE COMMA exp_pkexp_create_valid_char : COLUMN_OR_TABLE CHAR LPAREN COLUMN_OR_TABLE RPAREN UNIQUE\n                               | COLUMN_OR_TABLE CHAR LPAREN COLUMN_OR_TABLE RPARENexp_create_valid_int : COLUMN_OR_TABLE INT\n                            | COLUMN_OR_TABLE INT UNIQUEexp_create_valid_float : COLUMN_OR_TABLE FLOAT\n                              | COLUMN_OR_TABLE FLOAT UNIQUEexp_drop : DROP TABLE COLUMN_OR_TABLE \n                | DROP INDEX COLUMN_OR_TABLEexp_select : SELECT STAR FROM COLUMN_OR_TABLE END\n                  | SELECT STAR FROM COLUMN_OR_TABLE exp_conditionexp_delete : DELETE FROM COLUMN_OR_TABLE END\n                  | DELETE FROM COLUMN_OR_TABLE exp_conditionexp_insert : INSERT INTO COLUMN_OR_TABLE exp_insert_lineexp_insert_line : VALUES LPAREN columns RPAREN ENDcolumns : COLUMN_OR_TABLE\n               | COLUMN_OR_TABLE COMMA columnsexp_condition : WHERE exp_all_conditions ENDexp_all_conditions : COLUMN_OR_TABLE COMPARATOR COLUMN_OR_TABLE\n                          | COLUMN_OR_TABLE COMPARATOR COLUMN_OR_TABLE AND exp_all_conditionsexp_quit : QUITexp_execfile : EXECFILE'
    
_lr_action_items = {'DROP':([0,],[9,]),'SELECT':([0,],[10,]),'DELETE':([0,],[11,]),'CREATE':([0,],[12,]),'INSERT':([0,],[13,]),'QUIT':([0,],[14,]),'EXECFILE':([0,],[15,]),'$end':([1,2,3,4,5,6,7,8,14,15,23,24,31,32,36,38,39,52,67,78,84,],[0,-1,-2,-3,-4,-5,-6,-7,-38,-39,-25,-26,-29,-30,-31,-27,-28,-35,-8,-32,-9,]),'TABLE':([9,12,],[16,20,]),'INDEX':([9,12,],[17,21,]),'STAR':([10,],[18,]),'FROM':([11,18,],[19,25,]),'INTO':([13,],[22,]),'COLUMN_OR_TABLE':([16,17,19,20,21,22,25,33,34,35,51,53,58,60,64,69,72,73,83,],[23,24,26,27,28,29,30,41,42,50,62,63,42,70,74,76,62,41,76,]),'END':([26,30,40,57,63,71,77,80,],[31,38,52,67,-36,78,84,-37,]),'WHERE':([26,30,],[33,33,]),'LPAREN':([27,37,50,54,59,],[34,51,60,64,69,]),'ON':([28,],[35,]),'VALUES':([29,],[37,]),'PRIMARY':([34,58,],[49,49,]),'COMPARATOR':([41,],[53,]),'CHAR':([42,],[54,]),'INT':([42,],[55,]),'FLOAT':([42,],[56,]),'RPAREN':([43,44,45,46,47,48,55,56,61,62,65,66,68,70,74,75,76,79,81,82,85,86,],[57,-10,-12,-13,-14,-15,-21,-23,71,-33,-22,-24,-11,77,81,82,-17,-34,-20,-16,-19,-18,]),'COMMA':([44,45,46,47,48,55,56,62,65,66,76,81,82,85,],[58,-12,-13,-14,-15,-21,-23,72,-22,-24,83,-20,-16,-19,]),'KEY':([49,],[59,]),'UNIQUE':([55,56,81,],[65,66,85,]),'AND':([63,],[73,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'expression':([0,],[1,]),'exp_drop':([0,],[2,]),'exp_select':([0,],[3,]),'exp_delete':([0,],[4,]),'exp_create':([0,],[5,]),'exp_insert':([0,],[6,]),'exp_quit':([0,],[7,]),'exp_execfile':([0,],[8,]),'exp_condition':([26,30,],[32,39,]),'exp_insert_line':([29,],[36,]),'exp_all_conditions':([33,73,],[40,80,]),'exp_create_columns':([34,58,],[43,68,]),'exp_create_valid_column':([34,58,],[44,44,]),'exp_create_valid_char':([34,58,],[45,45,]),'exp_create_valid_int':([34,58,],[46,46,]),'exp_create_valid_float':([34,58,],[47,47,]),'exp_create_valid_pk':([34,58,],[48,48,]),'columns':([51,72,],[61,79,]),'exp_pk':([69,83,],[75,86,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> expression","S'",1,None,None,None),
  ('expression -> exp_drop','expression',1,'p_expression_start','interpreter.py',125),
  ('expression -> exp_select','expression',1,'p_expression_start','interpreter.py',126),
  ('expression -> exp_delete','expression',1,'p_expression_start','interpreter.py',127),
  ('expression -> exp_create','expression',1,'p_expression_start','interpreter.py',128),
  ('expression -> exp_insert','expression',1,'p_expression_start','interpreter.py',129),
  ('expression -> exp_quit','expression',1,'p_expression_start','interpreter.py',130),
  ('expression -> exp_execfile','expression',1,'p_expression_start','interpreter.py',131),
  ('exp_create -> CREATE TABLE COLUMN_OR_TABLE LPAREN exp_create_columns RPAREN END','exp_create',7,'p_expression_create','interpreter.py',134),
  ('exp_create -> CREATE INDEX COLUMN_OR_TABLE ON COLUMN_OR_TABLE LPAREN COLUMN_OR_TABLE RPAREN END','exp_create',9,'p_expression_create','interpreter.py',135),
  ('exp_create_columns -> exp_create_valid_column','exp_create_columns',1,'p_expression_create_columns','interpreter.py',155),
  ('exp_create_columns -> exp_create_valid_column COMMA exp_create_columns','exp_create_columns',3,'p_expression_create_columns','interpreter.py',156),
  ('exp_create_valid_column -> exp_create_valid_char','exp_create_valid_column',1,'p_expression_create_valid_column','interpreter.py',160),
  ('exp_create_valid_column -> exp_create_valid_int','exp_create_valid_column',1,'p_expression_create_valid_column','interpreter.py',161),
  ('exp_create_valid_column -> exp_create_valid_float','exp_create_valid_column',1,'p_expression_create_valid_column','interpreter.py',162),
  ('exp_create_valid_column -> exp_create_valid_pk','exp_create_valid_column',1,'p_expression_create_valid_column','interpreter.py',163),
  ('exp_create_valid_pk -> PRIMARY KEY LPAREN exp_pk RPAREN','exp_create_valid_pk',5,'p_expression_create_pk','interpreter.py',167),
  ('exp_pk -> COLUMN_OR_TABLE','exp_pk',1,'p_expression_pk','interpreter.py',171),
  ('exp_pk -> COLUMN_OR_TABLE COMMA exp_pk','exp_pk',3,'p_expression_pk','interpreter.py',172),
  ('exp_create_valid_char -> COLUMN_OR_TABLE CHAR LPAREN COLUMN_OR_TABLE RPAREN UNIQUE','exp_create_valid_char',6,'p_expression_create_valid_char','interpreter.py',176),
  ('exp_create_valid_char -> COLUMN_OR_TABLE CHAR LPAREN COLUMN_OR_TABLE RPAREN','exp_create_valid_char',5,'p_expression_create_valid_char','interpreter.py',177),
  ('exp_create_valid_int -> COLUMN_OR_TABLE INT','exp_create_valid_int',2,'p_expression_create_valid_int','interpreter.py',187),
  ('exp_create_valid_int -> COLUMN_OR_TABLE INT UNIQUE','exp_create_valid_int',3,'p_expression_create_valid_int','interpreter.py',188),
  ('exp_create_valid_float -> COLUMN_OR_TABLE FLOAT','exp_create_valid_float',2,'p_expression_create_valid_float','interpreter.py',198),
  ('exp_create_valid_float -> COLUMN_OR_TABLE FLOAT UNIQUE','exp_create_valid_float',3,'p_expression_create_valid_float','interpreter.py',199),
  ('exp_drop -> DROP TABLE COLUMN_OR_TABLE','exp_drop',3,'p_expression_drop','interpreter.py',210),
  ('exp_drop -> DROP INDEX COLUMN_OR_TABLE','exp_drop',3,'p_expression_drop','interpreter.py',211),
  ('exp_select -> SELECT STAR FROM COLUMN_OR_TABLE END','exp_select',5,'p_expression_select','interpreter.py',229),
  ('exp_select -> SELECT STAR FROM COLUMN_OR_TABLE exp_condition','exp_select',5,'p_expression_select','interpreter.py',230),
  ('exp_delete -> DELETE FROM COLUMN_OR_TABLE END','exp_delete',4,'p_expression_delete','interpreter.py',237),
  ('exp_delete -> DELETE FROM COLUMN_OR_TABLE exp_condition','exp_delete',4,'p_expression_delete','interpreter.py',238),
  ('exp_insert -> INSERT INTO COLUMN_OR_TABLE exp_insert_line','exp_insert',4,'p_expression_insert','interpreter.py',246),
  ('exp_insert_line -> VALUES LPAREN columns RPAREN END','exp_insert_line',5,'p_expression_insert_line','interpreter.py',256),
  ('columns -> COLUMN_OR_TABLE','columns',1,'p_expression_columns','interpreter.py',259),
  ('columns -> COLUMN_OR_TABLE COMMA columns','columns',3,'p_expression_columns','interpreter.py',260),
  ('exp_condition -> WHERE exp_all_conditions END','exp_condition',3,'p_expression_condition','interpreter.py',265),
  ('exp_all_conditions -> COLUMN_OR_TABLE COMPARATOR COLUMN_OR_TABLE','exp_all_conditions',3,'p_expression_all_conditions','interpreter.py',268),
  ('exp_all_conditions -> COLUMN_OR_TABLE COMPARATOR COLUMN_OR_TABLE AND exp_all_conditions','exp_all_conditions',5,'p_expression_all_conditions','interpreter.py',269),
  ('exp_quit -> QUIT','exp_quit',1,'p_expression_quit','interpreter.py',279),
  ('exp_execfile -> EXECFILE','exp_execfile',1,'p_expression_execfile','interpreter.py',285),
]