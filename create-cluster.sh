#!/bin/sh -e

if [ $# -ne 3 ] ; then
	echo "Usage: $0 <DNS_NAME> <nfs_server> <nfs_mount> <kubernetes_namespace>"
	echo "  example: $0 example.com 1.2.3.4 /vol_kubenfs9/ota default"
	exit 1
fi

DNS_NAME="$1"
SERVER_NAME="ota-ce.${DNS_NAME}"
NFS_SERVER=$2
NFS_MOUNT=$3
NAMESPACE=${4:-default}



echo "= Creating config/local.yaml"
cat >config/local.yaml <<EOF
# config/local.yaml
#
# I prefer to not use Ingress controllers in GKE for a few reasons:
# 1) They are still in beta.
# 2) They cost a little more than just doing a Service of type "loadBalancer".
# 3) When you deploy this securely, you'll need your own nginx reverse-proxy
#    that can handle authentication/authorization.
create_ingress: false

# In which namespace do you want to create the ota infrastructure and services
kube_namespace: ${NAMESPACE}

#NFS server and NFS mount details:
nfs_server: ${NFS_SERVER}
nfs_mount: ${NFS_MOUNT}

# We aren't using an Ingress, but templates/services/app.tmpl.yaml still
# uses this for building up the DNS names of the services it uses. This
# field must be set to the domain you host your service under. eg:
# ingress_dns_name: foundriez.io
ingress_dns_name: $DNS_NAME

# Use the 0.4 ota-tuf containers. They don't require "vault" which makes
# deployment and management of the cluster dramatically easier.
tuf_keyserver_daemon_docker_image: advancedtelematic/tuf-keyserver:0.4.0-46-g0298f0a
tuf_keyserver_docker_image: advancedtelematic/tuf-keyserver:0.4.0-46-g0298f0a
tuf_reposerver_docker_image: advancedtelematic/tuf-reposerver:0.4.0-46-g0298f0a

# The default constraints used by OTA CE aren't really sufficient for a
# usable cluster. These are somewhat arbitrary values that we've found work:
device_registry_java_opts: "-Xmx450m"
device_registry_mem: 500Mi

director_daemon_java_opts: "-Xmx450m"
director_daemon_mem: 500Mi

director_java_opts: "-Xmx700m"
director_mem: 750Mi

kafka_mem: 750Mi
kafka_disk: 20Gi

mysql_disk: 20Gi

treehub_java_opts: "-Xmx1750m"
treehub_mem: 2Gi
treehub_disk: 20Gi

tuf_keyserver_daemon_java_opts: "-Xmx450m"
tuf_keyserver_daemon_mem: 500Mi

tuf_keyserver_java_opts: "-Xmx700m"
tuf_keyserver_mem: 750Mi

tuf_reposerver_java_opts: "-Xmx700m"
tuf_reposerver_mem: 750Mi

zookeeper_mem: 500Mi
zookeeper_disk: 20Gi
EOF

#echo "= Creating cluster, should take about 3 minutes ..."
#./contrib/gke/gcloud container clusters create ota-ce \
     #--machine-type n1-standard-2 --num-nodes=5 --cluster-version=1.10.4-gke.3

#./contrib/gke/gcloud container clusters get-credentials ota-ce
#echo "calling make"
make check_dependencies
make SERVER_NAME=$SERVER_NAME NAMESPACE=${NAMESPACE} new-server

echo "= Running start-infra, should take about 3 minutes ..."
make start-infra

echo "= Running start-services, should take about 2 minutes ..."
make SERVER_NAME=$SERVER_NAME DNS_NAME=$DNS_NAME NAMESPACE=${NAMESPACE} start-services

chown -R $USER generated

echo "= Your cluster is up and running. Here are the pods:"
kubectl get pods -n ${NAMESPACE}

# echo
echo -n "= Waiting for public IP of reverse-proxy "
ip="null"
sleep 20
while [ "$ip" == "null" ] ; do
  ip=$(kubectl get svc reverse-proxy -n ${NAMESPACE} -o json | jq -r '.status.loadBalancer.ingress[0].ip')
  sleep 10s
  echo -n "."
done
echo
echo "  The reverse-proxy IP you need for DNS is: $ip"
