##This script should only be run 1 time unless the index needs to be recreated

from elasticsearch import Elasticsearch

#This is where you put the AWS Elasticsearch Endpoint
host_url = ['https://search-glos-metadata-jy4xxxs6o26fgmdj7guj32nvje.us-east-2.es.amazonaws.com']

#This will connect to the AWS Elasticsearch instance
es_conn = Elasticsearch(host_url)

###This is the index mapping which defines the fields, data types, and settings for the index
mapping = {
    'settings' : {
    "index.mapping.ignore_malformed": True},
    'metadata':{  
      'mappings':{  
         'record':{  
            'properties':{
             'schema':{  
                  'type':'text',
                  'ignore_malformed' : True,
                  'fields':{  
                     'keyword':{  
                        'type':'keyword',
                        'ignore_above':256
                     }
                  }
               },
               'uuid':{  
                  'type':'text',
                  'ignore_malformed' : True,
                  'fields':{  
                     'keyword':{  
                        'type':'keyword',
                        'ignore_above':256
                     }
                  }
               },
             'id':{  
                  'type':'text',
                  'ignore_malformed' : True,
                  'fields':{  
                     'keyword':{  
                        'type':'keyword',
                        'ignore_above':256
                     }
                  }
               },
              'title':{  
                  'type':'text',
                  'ignore_malformed' : True,
                  'fields':{  
                     'keyword':{  
                        'type':'keyword',
                        'ignore_above':256
                     }
                  }
               },
              'abstract':{  
                  'type':'string',
                  'ignore_malformed' : True,
                  'fields':{  
                     'keyword':{  
                        'type':'string'
                     }
                  }
               },
              'keyword':{  
                  'type':'string',
                  'ignore_malformed' : True,
                  'fields':{  
                     'keyword':{  
                        'type':'string',
                        'ignore_above':256
                     }
                  }
               },
              'link':{  
                  'type':'text',
                  'ignore_malformed' : True,
                  'fields':{  
                     'keyword':{  
                        'type':'keyword',
                        'ignore_above':256
                     }
                  }
               },
              'responsibleParty':{  
                  'type':'text',
                  'ignore_malformed' : True,
                  'fields':{  
                     'keyword':{  
                        'type':'keyword',
                        'ignore_above':256
                     }
                  }
               },
              'metadatacreationdate':{  
                  'type':'text',
                  'ignore_malformed' : True,
                  'fields':{  
                     'keyword':{  
                        'type':'keyword',
                        'ignore_above':256
                     }
                  }
               },
              'geoBox':{  
                  'type':'text',
                  'ignore_malformed' : True,
                  'fields':{  
                     'keyword':{  
                        'type':'keyword',
                        'ignore_above':256
                     }
                  }
               },
              'image':{  
                  'type':'text',
                  'ignore_malformed' : True,
                  'fields':{  
                     'keyword':{  
                        'type':'keyword',
                        'ignore_above':256
                     }
                  }
               },
               'LegalConstraints':{  
                  'type':'text',
                  'ignore_malformed' : True,
                  'fields':{  
                     'keyword':{  
                        'type':'keyword',
                        'ignore_above':256
                     }
                  }
               },
              'temporalExtent':{  
                  'type':'text',
                  'ignore_malformed' : True,
                  'fields':{  
                     'keyword':{  
                        'type':'keyword',
                        'ignore_above':256
                     }
                  }
               },
              'parentId':{  
                  'type':'text',
                  'ignore_malformed' : True,
                  'fields':{  
                     'keyword':{  
                        'type':'keyword',
                        'ignore_above':256
                     }
                  }
               },
               'datasetcreationdate':{  
                  'type':'text',
                  'ignore_malformed' : True,
                  'fields':{  
                     'keyword':{  
                        'type':'keyword',
                        'ignore_above':256
                     }
                  }
               },
               'Constraints':{  
                  'type':'text',
                  'ignore_malformed' : True,
                  'fields':{  
                     'keyword':{  
                        'type':'keyword',
                        'ignore_above':256
                     }
                  }
               },
                'SecurityConstraints':{  
                  'type':'text',
                  'ignore_malformed' : True,
                  'fields':{  
                     'keyword':{  
                        'type':'keyword',
                        'ignore_above':256
                     }
                  }
               }
            }
         }
      }
   }
}

#This line should only be run if the index needs to be recreated
#es_conn.indices.delete(index = 'metadata')

#This line creates the index using the parameters defined in the variable mapping
es_conn.indices.create(index = 'metadata', body = mapping)

print ('Index Created')

