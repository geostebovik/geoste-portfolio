// =============================================================================
// IIP -- M11 event subscription: BlobCreated in `uploads` -> queue upload-events
//
// Written by Claude, 2026-09-24. D-M11-1 (b) (Gerard, Sep 23): Event Grid
// delivers to a storage queue with the SYSTEM TOPIC'S OWN IDENTITY
// (deliveryWithResourceIdentity). No webhook, no function key, and no
// dependency on the Function's code being deployed first.
//
// Deployed AFTER rbac.bicep (main.bicep's dependsOn), because delivery needs
// row 14 (system topic -> Storage Queue Data Message Sender on the queue).
// A role assignment can take several minutes to propagate. Event Grid retries
// failed deliveries (default: 30 attempts over 24 h), so an early event is
// delayed, not lost.
// =============================================================================

param systemTopicName string
param dataStorageAccountName string
param uploadEventsQueueName string
param uploadsContainerName string

resource dataStorage 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: dataStorageAccountName
}

resource systemTopic 'Microsoft.EventGrid/systemTopics@2025-02-15' existing = {
  name: systemTopicName
}

resource uploadsToQueue 'Microsoft.EventGrid/systemTopics/eventSubscriptions@2025-02-15' = {
  parent: systemTopic
  name: 'evgs-uploads-to-queue'
  properties: {
    eventDeliverySchema: 'EventGridSchema'
    filter: {
      includedEventTypes: [
        'Microsoft.Storage.BlobCreated'
      ]
      // Only the uploads container. The Function writes to `results` on the
      // same account, so without this filter every result would trigger a run.
      subjectBeginsWith: '/blobServices/default/containers/${uploadsContainerName}/'
    }
    deliveryWithResourceIdentity: {
      identity: {
        type: 'SystemAssigned'
      }
      destination: {
        endpointType: 'StorageQueue'
        properties: {
          resourceId: dataStorage.id
          queueName: uploadEventsQueueName
        }
      }
    }
  }
}

output eventSubscriptionName string = uploadsToQueue.name
