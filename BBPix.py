import re, uuid, qrcode
import threading, time
from hashlib import md5
from json import dumps
from requests import Request, Session
from urllib3 import disable_warnings, exceptions
disable_warnings(exceptions.InsecureRequestWarning)


class PixBBOperations(object):
    ENVIRONMENT = ["hm.", ""]  # Homologação / Produção ..
    FULL_SCOPE = " ".join(["cob.write", "cob.read", "pix.read"])
    PIX_KEY_HM = [  # Chaves PIX de Homologação fornecidas pelo BB
        "7f6844d0-de89-47e5-9ef7-e0a35a681615",
        "3d94a38b-f344-460e-b6c9-489469b2fb03",
        "d14d32de-b3b9-4c31-9f89-8df2cec92c50"
    ]

    #make QrCode image
    def MakeQrCode(content, file=None):
        if not file:
            file = str(uuid.uuid4())[:5] + '.png'
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(content)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img.save(file)
        return file

    # executa requisições HTTP
    def RunRequest(type, url, headers, params, data={}, json={}):
        pix_request = Request(type,
                              url,
                              headers=headers,
                              params=params,
                              data=data,
                              json=json).prepare()
        response = (Session()).send(pix_request, verify=False)
        return response.status_code, response.json()

    # refaz a autenticação qdo for expirar
    def refresh_token(self):
        while self.logged:
            time.sleep(int(self.expires_in * 0.8))
            self.Login()
        raise Exception("Não foi possível pegar 1 novo token. Saindo...")

    # autenticar no sistema BB
    def Login(self):
        url = self.LoginRootURL + "/oauth/token"
        self.headers['Authorization'] = self.basic_token
        data = {'grant_type': 'client_credentials', "scope": self.scope}
        code, json = PixBBOperations.RunRequest("POST", url, self.headers,
                                                self.params, data, {})
        self.logged = False
        if code in [200]:
            self.logged = True
            self.access_token = json["access_token"]
            self.token_type = json["token_type"]
            self.expires_in = json["expires_in"]
            self.headers["accept"] = "application/json"
            self.headers["Authorization"] = "{} {}".format(
                self.token_type, self.access_token)
        return code in [200]

    # cria cobrança.
    def PixMakeCob(self, jsondata, makeqrcodeimage=True, txid=None):
        if not txid:
            txid = str(uuid.uuid4())
            txid = md5((txid + " " + dumps(jsondata)).encode('utf-8'))
            txid = re.sub("[^a-zA-Z0-9]", '', txid.hexdigest())[:35]
        # Gera uma cobrança PIX e retorna um Json SEM o campo de dados p/ Gerar o QRCode
        # url = "{}/pix/v1/cob/{}".format(self.RootURL, txid) # OLD!!!
        # Gera uma cobrança PIX e retorna um Json com campo de dados p/ Gerar o QRCode
        url = "{}/pix/v1/cobqrcode/{}".format(self.RootURL, txid)
        jsondata["chave"] = self.pix_key
        code, json = PixBBOperations.RunRequest("PUT", url, self.headers,
                                                self.params, {}, jsondata)
        if code in [200] and makeqrcodeimage and "textoImagemQRcode" in json:
            fqrcode = PixBBOperations.MakeQrCode(json["textoImagemQRcode"])
            return code, json, txid, fqrcode
        return code, json, txid, None

    # consulta uma cobrança
    def PixQueryCob(self, txid, review=0):
        url = "{}/pix/v1/cob/{}".format(self.RootURL, txid)
        parm = dict({"revisao": review}, **self.params)
        code, json = PixBBOperations.RunRequest("GET", url, self.headers, parm)
        return code, json

    # consultar Pix recebidos
    def PixReceivedQuery(self, dateini, dataend, txid):
        url = "{}/pix/v1/".format(self.RootURL)
        localdata = {
            "inicio": "{}T00:00:00Z".format(dateini),
            "fim": "{}T00:00:00Z".format(dataend),
            "txid": txid,
        }
        parm = dict(localdata, **self.params)
        code, json = PixBBOperations.RunRequest("GET", url, self.headers, parm)
        return code, json

    def __init__(
        self,
        app_key_dev,
        basic_token,
        env=None,
        scope=None,
        pix_key=None,
    ):
        super().__init__()
        if not app_key_dev:
            raise Exception(
                "informe a chave \"developer_application_key\" do APP.")
        self.app_key_dev = app_key_dev

        if not basic_token or "Basic " not in basic_token:  # example: "Basic AzdE..."
            raise Exception(
                "informe a chave \"basic\" do APP para autenticar no serviço do BB."
            )
        self.basic_token = basic_token

        environment = env
        if not environment:
            environment = PixBBOperations.ENVIRONMENT[0]

        self.scope = scope
        if not self.scope:
            self.scope = PixBBOperations.FULL_SCOPE

        self.pix_key = pix_key
        if not self.pix_key:
            self.pix_key = PixBBOperations.PIX_KEY_HM[0]
            environment = PixBBOperations.ENVIRONMENT[0]

        if environment == PixBBOperations.ENVIRONMENT[0]:
            self.params = {"gw-dev-app-key": self.app_key_dev}
        else:
            self.params = {"gw-app-key": self.app_key_dev}

        self.LoginRootURL = "https://oauth.{}bb.com.br".format(environment)
        self.RootURL = "https://api.{}bb.com.br".format(environment)
        self.headers = {'Content-Type': "application/x-www-form-urlencoded"}
        self.logged = False
        if not self.Login():
            raise Exception("Não foi possível logar.")
        else:  # Agenda para pegar um novo token qdo tiver perto de vencer
            th = threading.Thread(target=self.refresh_token)
            th.daemon = True
            th.start()
