local-internet-simulation/
│
├── layers/
│ ├── link_layer.py
│ ├── internet_layer.py
│ ├── transport_layer.py
│ ├── application_layer.py
│
├── protocols/
│ ├── http_server.py
│ ├── http_client.py
│ ├── ftp_server.py
│ ├── ftp_client.py
│ ├── smtp_server.py
│ ├── smtp_client.py
│
├── routing/
│ ├── router.py
│ ├── routing_table.json
│
├── security/
│ ├── tls_server.py
│ ├── tls_client.py
│ ├── cert.pem
│ ├── key.pem
│
├── dns/
│ ├── dns_server.py
│ ├── dns_records.json
│
├── network_conditions/
│ ├── packet_loss.py
│ ├── delays.py
│ ├── congestion.py
│
├── utils/
│ ├── helpers.py
│ ├── constants.py
│
├── tests/
│ ├── test_link_layer.py
│ ├── test_internet_layer.py
│ ├── test_transport_layer.py
│ ├── test_application_layer.py
│ ├── test_routing.py
│ ├── test_dns.py
│ ├── test_tls.py
│
├── main.py
├── README.md
├── requirements.txt
