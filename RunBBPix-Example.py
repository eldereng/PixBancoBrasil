from BBPix import PixBBOperations

pix = PixBBOperations(
    app_key_dev="daaaaa",
    basic_token="Basic xyz"
)

data = {
    "calendario": {
        "expiracao": "3600"
    },
    "valor": {
        "original": "15.23"
    },
    #"chave": "", ## Não precisa informar
    "solicitacaoPagador": "asdasdasds."
}
code, json, txid, qrcode = pix.PixMakeCob(data, makeqrcodeimage=True)
print(json["textoImagemQRcode"])
print(code, json, txid, qrcode)
print("")

code, json = pix.PixQueryCob(txid)
print(code, json)
print("")

code, json = pix.PixReceivedQuery("2021-01-11", "2021-01-17", txid)
print(code, json)
print("")

