# Parameters

PUBLISHER = publisher
RETRIEVER = retriever
BROKER = broker

SOURCES_PUBLISHER.c = 
SOURCES_PUBLISHER.h = 
SOURCES_RETRIEVER.c = 
SOURCES_RETRIEVER.h = 
SOURCES_BROKER.c = 
SOURCES_BROKER.h = 
SOURCES.x = dataspace.x

TARGETS_BROKER.c = dataspace_svc.c broker.c dataspace_xdr.c 
TARGETS_PUBLISHER.c = dataspace_clnt.c publisher.c dataspace_xdr.c 
TARGETS_RETRIEVER.c = dataspace_clnt.c retriever.c dataspace_xdr.c
TARGETS_GENERATED = dataspace.h dataspace_xdr.c dataspace_clnt.c dataspace_svc.c
TARGETS = $(TARGETS_GENERATED) publisher.c retriever.c broker.c

BUNDLE = $(SOURCES.x) $(TARGETS) README Makefile khash.h kvec.h

OBJECTS_BROKER = $(SOURCES_BROKER.c:%.c=%.o) $(TARGETS_BROKER.c:%.c=%.o)
OBJECTS_PUBLISHER = $(SOURCES_PUBLISHER.c:%.c=%.o) $(TARGETS_PUBLISHER.c:%.c=%.o)
OBJECTS_RETRIEVER = $(SOURCES_RETRIEVER.c:%.c=%.o) $(TARGETS_RETRIEVER.c:%.c=%.o)

# Compiler flags 

CFLAGS += -g -I /usr/include/tirpc -std=c23
LDLIBS += -ltirpc

RPCGENFLAGS = 

# Targets 

all : $(PUBLISHER) $(RETRIEVER) $(BROKER)

bundle:
	zip booher_hw2.zip $(BUNDLE)

$(TARGETS) : $(SOURCES.x) 
	rpcgen $(RPCGENFLAGS) $(SOURCES.x)

$(OBJECTS_PUBLISHER) : $(SOURCES_PUBLISHER.c) $(SOURCES_PUBLISHER.h) $(TARGETS_PUBLISHER.c) 
$(OBJECTS_RETRIEVER) : $(SOURCES_RETRIEVER.c) $(SOURCES_RETRIEVER.h) $(TARGETS_RETRIEVER.c) 
$(OBJECTS_BROKER) : $(SOURCES_BROKER.c) $(SOURCES_BROKER.h) $(TARGETS_BROKER.c) 

$(PUBLISHER) : $(OBJECTS_PUBLISHER) 
	$(LINK.c) -o $(PUBLISHER) $(OBJECTS_PUBLISHER) $(LDLIBS) 

$(RETRIEVER) : $(OBJECTS_RETRIEVER) 
	$(LINK.c) -o $(RETRIEVER) $(OBJECTS_RETRIEVER) $(LDLIBS) 

$(BROKER) : $(OBJECTS_BROKER) 
	$(LINK.c) -o $(BROKER) $(OBJECTS_BROKER) $(LDLIBS)

 clean:
	 $(RM) core $(TARGETS_GENERATED) $(OBJECTS_PUBLISHER) $(OBJECTS_RETRIEVER) $(OBJECTS_BROKER) $(PUBLISHER) $(RETRIEVER) $(BROKER)

