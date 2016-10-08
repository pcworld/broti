FROM base/archlinux
MAINTAINER Stefan Koch

RUN pacman -Sy --noconfirm \
    python-virtualenv \
    sqlite \
    openssl
RUN useradd -m -s /bin/sh broti
COPY broti /home/broti/broti
COPY requirements.txt /home/broti/
RUN cd /home/broti \
    && virtualenv -p python3 env \
    && source env/bin/activate \
    && pip install -r requirements.txt \
    && cd broti

# TODO: Add real command to execute broti when it is possible
# without being in broti folder
CMD ["/bin/bash"]
