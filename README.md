- > On the first time

	- > python -m venv .env

	- > Install packages

		- > pip install -r requirements.txt 

- > Always run

	- > conda deactivate & deactivate

	- > .env\Scripts\activate.bat

- > Include your keys on file "RunBBPix-Example.py"

	- > developer_application_key = app_key_dev

	- > Basic = basic_token
	
	- > Get these keys on https://app.developers.bb.com.br

- > To test, run

	- > python RunBBPix-Example.py

- > Out put Example

	-> PixMakeCob
```json
{
	'status': 'ATIVA',
	'calendario': {
		'criacao': '2021-01-14T16: 45: 46.7184860000',
		'expiracao': '3600'
	},
	'location': 'qrcodepix-h.bb.com.br/pix/v2/997d94de-6e9a-4e07-be53-8a64544935bf',
	'textoImagemQRcode': '00020101021226870014br.gov.bcb.pix2565qrcodepix-h.bb.com.br/pix/v2/997d94de-6e9a-4e07-be53-8a64544935bf520400005303986540515.235802BR5920ALANGUIACHEROBUENO6008BRASILIA62070503***6304E21D',
	'txid': '8519236e46f0900dc64de96fc5289649',
	'revisao': 0,
	'devedor': {
		'nome': ''
	},
	'valor': {
		'original': '15.23'
	},
	'chave': '7f6844d0-de89-47e5-9ef7-e0a35a681615',
	'solicitacaoPagador': 'asdasdasds.'
}
```
