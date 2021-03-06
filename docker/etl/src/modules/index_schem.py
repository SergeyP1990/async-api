
def index_settings() -> dict:
    d = {
        "settings": {
            "refresh_interval": "1s",
            "analysis": {
                "filter": {
                    "english_stop": {
                        "type":       "stop",
                        "stopwords":  "_english_"
                    },
                    "english_stemmer": {
                        "type": "stemmer",
                        "language": "english"
                    },
                    "english_possessive_stemmer": {
                        "type": "stemmer",
                        "language": "possessive_english"
                    },
                    "russian_stop": {
                        "type":       "stop",
                        "stopwords":  "_russian_"
                    },
                    "russian_stemmer": {
                        "type": "stemmer",
                        "language": "russian"
                    }
                },
                "analyzer": {
                    "ru_en": {
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "english_stop",
                            "english_stemmer",
                            "english_possessive_stemmer",
                            "russian_stop",
                            "russian_stemmer"
                        ]
                    }
                }
            }
        }
    }
    return d

def movies_index() -> dict:
    mappings = {
        "mappings": {
            "dynamic": "strict",
            "properties": {
                "uuid": {
                    "type": "keyword"
                },
                "imdb_rating": {
                    "type": "float"
                },
                "genre": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "uuid": {
                            "type": "keyword"
                        },
                        "name": {
                            "type": "text",
                            "analyzer": "ru_en"
                        }
                    }
                },
                "title": {
                    "type": "text",
                    "analyzer": "ru_en",
                    "fields": {
                        "raw": {
                            "type":  "keyword"
                        }
                    }
                },
                "description": {
                    "type": "text",
                    "analyzer": "ru_en"
                },
                "directors": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "uuid": {
                            "type": "keyword"
                        },
                        "full_name": {
                            "type": "text",
                            "analyzer": "ru_en"
                        }
                    }
                },
                "actors": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "uuid": {
                            "type": "keyword"
                        },
                        "full_name": {
                            "type": "text",
                            "analyzer": "ru_en"
                        }
                    }
                },
                "writers": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "uuid": {
                            "type": "keyword"
                        },
                        "full_name": {
                            "type": "text",
                            "analyzer": "ru_en"
                        }
                    }
                }
            }
        }
    }
    mappings_settings = dict(mappings, **index_settings())
    return mappings_settings

def genres_index() -> dict:
    mappings = {
        "mappings": {
            "dynamic": "strict",
            "properties": {
                "uuid": {
                    "type": "keyword"
                },
                "name": {
                    "type": "text",
                    "analyzer": "ru_en"
                }
            }
        }
    }
    mappings_settings = dict(mappings, **index_settings())
    return mappings_settings

def persons_index() -> dict:
    mappings = {
        "mappings": {
            "dynamic": "strict",
            "properties": {
                "uuid": {
                    "type": "keyword"
                },
                "full_name": {
                    "type": "text",
                    "analyzer": "ru_en"
                },
                "role": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "uuid": {
                            "type": "keyword"
                        },
                        "role": {
                            "type": "text",
                            "analyzer": "ru_en"
                        }
                    }
                },
                "film_ids": {
                    "type": "keyword"
                },
            }
        }
    }
    mappings_settings = dict(mappings, **index_settings())
    return mappings_settings