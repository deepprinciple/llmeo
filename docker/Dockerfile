FROM continuumio/miniconda3

ENV http_proxy http://100.68.166.13:3128
ENV https_proxy http://100.68.166.13:3128

ENV HTTP_PROXY http://100.68.166.13:3128
ENV HTTPS_PROXY http://100.68.166.13:3128

RUN apt-get update && apt-get install -y git

# Prep directory structure
WORKDIR /deep-principle
RUN mkdir dp-proj-llmeo
COPY . dp-proj-llmeo/

# Prep directory as git repo for setuptools version
RUN git init

WORKDIR /deep-principle/dp-proj-llmeo

# Install dependencies
RUN conda env create -vv -f environment.yml && conda clean -afy

RUN /opt/conda/envs/llmeo/bin/pip install -e .

RUN echo "source activate llmeo" > ~/.bashrc
ENV PATH /opt/conda/envs/llmeo/bin:$PATH
