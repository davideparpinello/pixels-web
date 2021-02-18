# Pixels - Progetto di comunicazioni multimediali

Repo contenente il server web in Node.js e gli script Python per il progetto del corso di Comunicazioni Multimediali (DISI Unitn, A.A. 2020/21)
## Membri
- Alessandro Ferronato (203110)
- Giorgia Giro (201725)
- Davide Parpinello (201494)
- Martina Peruzzo (204789)

> <b>Attenzione:</b> il server è configurato per essere eseguito solamente in localhost.

## [Link al report](./Report%20Pixels.pdf)

## Requisiti
- Node.js e NPM
- Python 3 e `python3-pip`, installare i moduli seguenti
  - modulo `json`
  - modulo `numpy`
  - modulo `opencv-python`
  - modulo `requests`
  - modulo `scikit-image`
  - modulo `matplotlib`
  - modulo `torch`

> Se l'installazione di `opencv-python` dovesse bloccarsi durante il build wheel eseguire prima il seguente comando `pip3 install --upgrade setuptools pip`

## Esecuzione del software
Per eseguire il server, installare prima le dipendenze di Node.js con il comando `npm install`.
Successivamente sarà possibile far partire il server Node.js con il comando `node index.js`.
Infine, eseguire il servizio Python con il comando `python3 pixels.py`