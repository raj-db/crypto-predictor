kubectl run kafka-tools --image=bitnami/kafka:latest -it --rm --restart=Never -- bash -c "\
  kafka-topics.sh --bootstrap-server kafka-e11b-kafka-bootstrap.kafka.svc.cluster.local:9092 --delete --topic candles-default-changelog && exit" && \
kubectl get pods -l app=candles -o name | xargs -I {} kubectl exec {} -- rm -rf /app/state/quixstreams-default && \
kubectl delete pod -l app=candles
