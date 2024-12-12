 #!/bin/bash
 
 gcloud functions deploy docsend2pdf \
     --gen2 \
     --runtime=python312 \
     --region=us-central1 \
     --source=. \
     --entry-point=docsend_http \
     --trigger-http \
     --memory=2048MB \
     --allow-unauthenticated
