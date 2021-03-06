FROM base/archlinux
MAINTAINER Stefan Koch

RUN pacman -Sy --noconfirm \
    python-virtualenv \
    sqlite \
    openssl
RUN useradd -m -s /bin/sh broti
COPY broti /home/broti/broti
COPY requirements.txt setup.py config.ini /home/broti/
RUN chown -R broti:broti /home/broti \
    && su broti -c 'cd /home/broti \
    && virtualenv -p python3 env \
    && source env/bin/activate \
    && pip install -r requirements.txt \
    && python setup.py install'

ENTRYPOINT ["su", "broti", "-c", "/bin/sh -c 'source /home/broti/env/bin/activate; /home/broti/env/bin/broti bot /home/broti/config.ini'"]
