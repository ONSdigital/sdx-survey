from google.cloud import pubsub_v1


project_id = "ons-sdx-sandbox"
topic_id = "dap-topic"

dap_publisher = pubsub_v1.PublisherClient()
# The `topic_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/topics/{topic_id}`
dap_topic_path = dap_publisher.topic_path(project_id, topic_id)


receipt_publisher = pubsub_v1.PublisherClient()
receipt_topic_path = receipt_publisher.topic_path(project_id, topic_id)
