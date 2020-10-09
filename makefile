# default target
html:

# distribution targets
dist:
	python3 setup.py sdist bdist_wheel

# XXX seem to need to distclean before doing pip install .
distclean: clean
	$(RM) -rf build dist $(wildcard *.egg-info)

# docker targets
DOCKER-ORG = broadbandforum
DOCKER-NAME = obbaa-vomci
DOCKER-TAG = latest
DOCKER-IMAGE = $(DOCKER-ORG)/$(DOCKER-NAME):$(DOCKER-TAG)
DOCKER-CMD = bash

DOCKER-BUILDOPTS =
ifneq "$(FROM)" ""
  DOCKER-BUILDOPTS += --build-arg FROM=$(FROM)
endif
ifneq "$(NOCACHE)" ""
  DOCKER-BUILDOPTS += --no-cache
endif

# https://superuser.com/questions/1301499/
#	  running-wireshark-inside-a-centos-docker-container
DOCKER-RUNOPTS = -p 12345:12345/udp \
		 --cap-add=NET_RAW --cap-add=NET_ADMIN

docker-build:
	docker image build $(DOCKER-BUILDOPTS) --tag=$(DOCKER-NAME) .
	docker image build -f proxy/Dockerfile $(DOCKER-BUILDOPTS) --tag=obbaa-vproxy:latest .

docker-push: docker-build
	docker image push $(DOCKER-IMAGE)

docker-pull:
	docker image pull $(DOCKER-IMAGE)

docker-run:
	docker container run -it --name $(DOCKER-NAME) --rm $(DOCKER-RUNOPTS) $(DOCKER-IMAGE) $(DOCKER-CMD)

docker-exec:
	docker container exec -it $(DOCKER-NAME) $(DOCKER-CMD)

# sphinx-build handles remaining targets; make help to get a list
%:
	@sphinx-build -M $@ . docs -T
