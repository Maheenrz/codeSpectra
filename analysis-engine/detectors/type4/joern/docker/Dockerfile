FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive


# Install required packages and set up UTF-8 locale
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk \
    curl \
    wget \
    unzip \
    locales \
    && rm -rf /var/lib/apt/lists/*

# Generate and set UTF-8 locale for Java/Joern
RUN locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

WORKDIR /opt/joern

RUN curl -L "https://github.com/joernio/joern/releases/latest/download/joern-install.sh" -o joern-install.sh \
    && chmod +x joern-install.sh \
    && ./joern-install.sh --install-dir=/opt/joern \
    && rm joern-install.sh

ENV PATH="/opt/joern/joern-cli:${PATH}"

RUN mkdir -p /workspace /output

WORKDIR /workspace

CMD ["tail", "-f", "/dev/null"]