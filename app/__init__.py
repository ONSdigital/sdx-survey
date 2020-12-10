from google.cloud import pubsub_v1


project_id = "ons-sdx-sandbox"
dap_topic_id = "dap-topic"
receipt_topic_id = "receipt_topic"

dap_publisher = pubsub_v1.PublisherClient()
# The `topic_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/topics/{topic_id}`
dap_topic_path = dap_publisher.topic_path(project_id, dap_topic_id)


receipt_publisher = pubsub_v1.PublisherClient()
receipt_topic_path = receipt_publisher.topic_path(project_id, receipt_topic_id)


# Subscriber setup
subscription_id = "survey-subscription"

subscriber = pubsub_v1.SubscriberClient()
# The `subscription_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/subscriptions/{subscription_id}`
subscription_path = subscriber.subscription_path(project_id, subscription_id)