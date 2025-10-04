# Almoxarifado
Código do Almoxarifado da Escola
Traceback (most recent call last):
  File "C:\Users\est.eletronica1\Desktop\almox_lourenco\emprestimos.py", line 78, in importar_emprestimos
    conexao.commit()
    ~~~~~~~~~~~~~~^^
  File "C:\Users\est.eletronica1\AppData\Local\Programs\Python\Python313\Lib\site-packages\mysql\connector\connection_cext.py", line 604, in commit
    self.handle_unread_result()
    ~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\est.eletronica1\AppData\Local\Programs\Python\Python313\Lib\site-packages\mysql\connector\connection_cext.py", line 1121, in handle_unread_result
    raise InternalError("Unread result found")
mysql.connector.errors.InternalError: Unread result found

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\est.eletronica1\Desktop\almox_lourenco\emprestimos.py", line 83, in importar_emprestimos
    if conexao.is_connected():
       ~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\est.eletronica1\AppData\Local\Programs\Python\Python313\Lib\site-packages\mysql\connector\connection_cext.py", line 413, in is_connected      
    self.handle_unread_result()
    ~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\est.eletronica1\AppData\Local\Programs\Python\Python313\Lib\site-packages\mysql\connector\connection_cext.py", line 1121, in handle_unread_result
    raise InternalError("Unread result found")
mysql.connector.errors.InternalError: Unread result found

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\est.eletronica1\Desktop\almox_lourenco\emprestimos.py", line 99, in <module>
    importar_emprestimos('em_ficha_202510032159.csv')
    ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\est.eletronica1\Desktop\almox_lourenco\emprestimos.py", line 94, in importar_emprestimos
    cursor.close()
    ~~~~~~~~~~~~^^
  File "C:\Users\est.eletronica1\AppData\Local\Programs\Python\Python313\Lib\site-packages\mysql\connector\cursor_cext.py", line 513, in close
    self._connection.handle_unread_result()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\est.eletronica1\AppData\Local\Programs\Python\Python313\Lib\site-packages\mysql\connector\connection_cext.py", line 1121, in handle_unread_result
    raise InternalError("Unread result found")
mysql.connector.errors.InternalError: Unread result found
