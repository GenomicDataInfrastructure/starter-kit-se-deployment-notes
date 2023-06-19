# Deployment of GDI starter kit

This repository is a collection of scripts and documentation produced during the deployment of the GDI starter kit in the Swedish node. However, it should not be used as a standalone guide, and it probably lacks some steps not documented during the deployment.

The deployment described here was done in one VM (virtual machine) and the services were deployed in docker containers. The VM is running behind an ha-proxy, which was used to route the traffic to the different services. The VM is running Ubuntu 22.04 LTS.

## Repos in the deployment

The repositories used in the deployment are the following:
1. https://github.com/GenomicDataInfrastructure/starter-kit-storage-and-interfaces.git
2. https://github.com/GenomicDataInfrastructure/starter-kit-htsget 
3. https://github.com/GenomicDataInfrastructure/starter-kit-rems
4. https://github.com/GenomicDataInfrastructure/starter-kit-containerized-computation
5. https://github.com/GenomicDataInfrastructure/starter-kit-beacon2-ri-api.git 

# User facing services
The user facing services are the following:
1. Download
2. Htsget
3. REMS
4. Login/Auth
5. Inbox
6. Beacon
7. Public key endpoint

The ports for these services should be open, in order to be able to access them from outside the VM. The ports in the Swedish case are:
1. Download: 8443
2. Htsget: 8081
3. REMS: 3000
4. Login/Auth: 8080
5. Inbox: 8000
6. Beacon: 8085 TODO: Change to the actual port
7. Public key endpoint: stored at an S3 bucket in the Swedish case

# LS AAI registration
In order to gain access to the LS AAI and enable the users to login with their home organization credentials, the Auth and REMS services need to be registered with LS AAI. Both of them can be under the same service since you are allowed to have multiple Redirect URIs (one for the Auth and one for the REMS). The registration process is described [here](https://docs.google.com/document/d/17pNXM_psYOP5rWF302ObAJACsfYnEWhjvxAHzcjvfIE/edit)

The details for the LS AAI configuration are described [here](https://lifescience-ri.eu/ls-login.html). For more information contact Dominic František Bučík on GDI slack.

## Create certificates for all these services
The user facing services are running with TLS encryption. To create the certificates, we used Certbot. The certificates are stored in a Docker volume, which is mounted in all the containers.

Clone the `storage-and-interfaces` repository using the following command:
```bash
git clone https://github.com/GenomicDataInfrastructure/starter-kit-storage-and-interfaces.git
```

Generate a certificate for all external facing services with a command similar to this (be sure to change the email and the domains):
```bash
certbot certonly --standalone \
        --noninteractive \
        --agree-tos \ 
        --preferred-challenges http \
        --email sda-ops@nbis.se \
        -d htsget.gdi.nbis.se \
        -d login.gdi.nbis.se \
        -d download.gdi.nbis.se \
        -d beacon.gdi.nbis.se \
        -d inbox.gdi.nbis.se \
        -d rems.gdi.nbis.se --expand
```

To renew the certificates and copy them to the Docker volume, run the following command or add it to the Certbot cron job, for example:
```none
1 2	1 * * root /usr/bin/certbot renew --deploy-hook /home/ubuntu/starter-kit-storage-and-interfaces/scripts/cert-deploy --quiet --no-self-upgrade
```

## Deploying storage and interfaces
Now that the storage and interfaces repository is cloned, start by editing the `config/config.yml` file (a sample can be found under `storage-and-interfaces/config` in this repository) and add the certificates you generated to the `app` entry (which is the download service), like:
```yaml
app: # this is for download
  host: "0.0.0.0"
  servercert: /shared/cert/fullchain.pem
  serverkey: /shared/cert/privkey.pem
  port: "8443"
```

And to the `s3inbox` entry in the `docker-compose.yml` file (a sample can be found under `storage-and-interfaces` in this repository) like:
```yaml
s3inbox:
  environment:
    - SERVER_CERT=/shared/cert/fullchain.pem
    - SERVER_KEY=/shared/cert/privkey.pem
```

### Deploying auth
Auth is a service in the storage-and-interfaces Docker compose file that enables the users to extract a token and an s3config file in order to download and upload data, respectively. 
In the `docker-compose.yml` file, apart from the credentials of the LS AAI account (registered in earlier steps), you should also set the redirect URL, to something like:
```yaml
- ELIXIR_REDIRECTURL=https://login.gdi.nbis.se/elixir/login
```
while the values for `ELIXIR_ID` and `ELIXIR_SECRET` can be obtained from `spreg`, in the Swedish case from `https://services.aai.lifescience-ri.eu/spreg/auth/facilities/detail/<YOUR_PROJECT_ID>`

### Storage
The Swedish deployment is using an external S3 backend for storing the files. However, the Docker compose file in storage-and-interfaces contains a Minio instance, that can be used for archiving the data. In either case, set the credentials of the S3 backend in the `config/config.yaml` file, specifically the `S3AccessKey` and `S3SecretKey` values.

### Update the issuer configuration
In `config/iss.json` there exists a file that defines the issuer that will be used from the download service. Change this to point to your REMS instance, for example:
```json
{
    "iss": "https://rems.gdi.nbis.se/",
    "jku": "https://rems.gdi.nbis.se/api/jwk"
}
```

## Deploying htsget
To get the `htsget` working with TLS, move to the `start-kit-htsget` directory and edit the `htsget-config/config.json` file (a sample can be found under `htsget/config-htsget/` in this repository) and change the location of `serverCert` and `serverKey` to:
```json
"serverCert": "/shared/cert/fullchain.pem",
"serverKey": "/shared/cert/privkey.pem"
```

And change the first source to point to the download endpoint. For example:
```json
{
    "pattern": "^s3/(?P<accession>.*)$",
    "path": "https://download.gdi.nbis.se/s3/{accession}"
},
```

Then change the port where the service is mapped to the port you want to expose (currently set to 8081) by changing the `docker-compose-htsget.yml` file (a sample can be found under `htsget` in this repository) as follows:
```yaml
services:
  server:
    ports:
      - 8081:3000
```

## Deploying REMS
Edit the configuration file `config.edn`, add/modify values for `public_url`, `database_url`, `oidc-metadata-url`, `oidc-scopes`, `oidc-client-id` and `oidc-client-secret`.
```edn
:public-url "https://rems.gdi.nbis.se/"
:database-url "postgresql://db:5432/rems?user=<REMS_DATABASE_USER>&password=<REMS_DATABASE_PASSWORD>"
:oidc-metadata-url "https://login.elixir-czech.org/oidc/.well-known/openid-configuration"
:oidc-scopes "openid profile email ga4gh_passport_v1"
```

The values for `oidc-client-id` and `oidc-client-secret` can be obtained from `spreg`, as mentioned in the Auth service deployment above.

To configure TLS for REMS, one needs to add three parameters, namely `ssl-port`, `ssl-keystore` and `ssl-keystore-password`. The value of `ssl-port` should be set as 3000, consequently, port for non-TLS can be modified to e.g. 3001.

The keystore file can be converted from certificate files generated by Certbot by the following commands, assuming the public key file is `./certs/cert.pem`, the private key file is `./certs/privkey.pem` and the CA file is `./certs/fullchain.pem`.

From outside of the container (on the VM) and under the root folder of the repository, run
```bash
openssl pkcs12 -export \
    -in ./certs/fullchain.pem \
    -inkey ./certs/privkey.pem \
    -out ./certs/rems.gdi.nbis.se.p12 \
    -name rems.gdi.nbis.se \
    -password "<CERTIFICATE_PASSWORD>"
```

Then run the following command from inside the REMS container:
```bash
keytool -importkeystore \
    -deststorepass <CERTIFICATE_PASSWORD> \
    -destkeypass <CERTIFICATE_PASSWORD> \
    -deststoretype pkcs12 \
    -srckeystore rems.gdi.nbis.se.p12 \
    -srcstoretype PKCS12 \
    -srcstorepass <CERTIFICATE_PASSWORD> \
    -destkeystore rems.gdi.nbis.se.keystore \
    -alias rems.gdi.nbis.se
```

For the Docker setup, add/modify ports of the service `app`
```yaml
ports:
- "3000:3000"
- "3001:3001"
```

Modify ports of the service `db` to 5433 to avoid conflict with any other database container 
```yaml
ports:
- "127.0.0.1:5433:5432"
```

Add the volume `starter-kit-storage-and-interfaces_shared`
```yaml
starter-kit-storage-and-interfaces_shared:
  external: true
```

The `private-key.jwk` created when deploying REMS does not contain the `kid` field, therefore (for now) that needs to be added manually, by copying the same value from the `public-key.jwk`. This might have been fixed on the [key creation script](https://github.com/GenomicDataInfrastructure/starter-kit-rems/blob/main/generate_jwks.py) in later REMS versions.

### Create an administrator account
In order to use REMS you need to create an admin account. Details about that can be found [here](https://github.com/GenomicDataInfrastructure/starter-kit-rems#get-admin-access).

### Create the robot account
After deploying REMS, create a robot user account, that will be used for the connection with the LS AAI. Details can be found [here](https://github.com/GenomicDataInfrastructure/starter-kit-rems#create-a-robot-user-and-an-api-key)

### Connect REMS to LS AAI
After setting up the robot account, send the required information to the LS AAI people. The data includes:
```yaml
- jwks url: https://rems.gdi.nbis.se/api/jwk
- permissions api: https://rems.gdi.nbis.se/api/permissions/<lifescience_user_id>
- user: <ROBOT_USER_NAME>
- user api key: <taken_from_REMS_database>
```
* The `lifescience_user_id` is not a specific value. It will be used from the LS AAI when requesting permissions.
* The user API key is created in the previous step. In order to extract it from the database, run 
```bash
docker exec -it rems_db psql -U rems -h localhost -c 'select * from api_key' rems
```
and get the key created for the robot account.


If everything worked well, you should be able to see the visas created by REMS in the token provided by the LS AAI for a specific user.

### Using REMS
In order to use REMS and be able to apply for access, you need to follow the steps described [here](https://github.com/GenomicDataInfrastructure/starter-kit-rems#create-your-own-data). This guide assumes that there exists an organisation, workflow etc.

## Deploying Beacon2

Clone the starter-kit-beacon2-ri-api repo using the following command:
```bash
git clone https://github.com/GenomicDataInfrastructure/starter-kit-beacon2-ri-api.git
```

Deployment instructions are available in the repo, at `https://github.com/GenomicDataInfrastructure/starter-kit-beacon2-ri-api/blob/master/deploy/README.md` 

There are some port collisions with storage-and-interfaces in this repo:
```none
9000 is used for beacon_training_ui
8081 is used for mongo-express
8000 is used for keycloak
```

In the Swedish case, changed these are:
```none
9000 → 9090
8081 → 8082
8000 → 8083
```
The new ports are included in the sample `beacon/docker-compose.yml` file. The `/beacon/permissions/auth.py` file (located in `permissions` folder of the `Beacon` repository) needs to be updated with the credentials of the LS AAI. Finally, the `/beacon/permissions/permissions.py` file (located in `permissions` folder of the `Beacon` repository) needs to be changed, by adding a user that should have access to a number of datasets. In the example, the user `<SOME_LS_AAI_USER>` is given access to the test dataset that will be added after starting the services. The `<SOME_LS_AAI_USER>` is the `preferred_username` returned by LS AAI when querying the user-info endpoint.

In order to connect to the Beacon Network, update the `deploy/conf.py` file and specifically the values under the sections `Beacon general info`, `Project info` and `Service` to reflect the information of the organisation. Apart from that, update also the section `Web server configuration` to add the certificates for the TLS connection. Notice that the value of `uri` should include a trailing slash `/`, otherwise the URLs from the Beacon Network will not be correct. Once the configuration is done, share the link of the beacon with the Beacon Network people, so that they can add it to the network.

NOTE: To run the beacon behind an nginx server with TLS termination, remove the port mapping from the beacon container, and create a new nginx container (included in the `docker-compose.yml` file here) like this:

```yaml
  # Nginx TLS proxy
  nginx:
    image: nginx:mainline-alpine3.17-slim
    depends_on:
      beacon:
        condition: service_started
    ports:
      - 5050:443
    volumes:
      - ./tls_nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - starter-kit-storage-and-interfaces_shared:/shared
    networks:
      - my-app-network

volumes:
  starter-kit-storage-and-interfaces_shared:
    external: true
```

and create the `tls_nginx.conf` (included in the `tls_nginx.conf` file under `beacon` in this repository) file as:
```
server {
    listen              443 ssl;
    server_name         localhost <hostname>;
    ssl_certificate     /shared/etc/letsencrypt/live/<cert-name>/fullchain.pem;
    ssl_certificate_key /shared/etc/letsencrypt/live/<cert-name>/privkey.pem;

    location / {
        proxy_pass http://beacon:5050/;
    }

}
```

Now that all the files are updated, the images need to be built and the services can be started with: 
```bash
docker compose up --build -d
```

Follow the instructions in the repository for loading the data, summarized:
```bash
for collection in datasets analyses biosamples cohorts genomiVariations individuals runs
do
    docker cp "./data/$collection.json" "deploy-db-1:/tmp/$collection.json"
    
    docker exec deploy-db-1 mongoimport --jsonArray \
        --uri 'mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin' \
        --file "/tmp/$collection.json" --collection "$collection"
done
```

And finally
```bash
docker exec beacon python beacon/reindex.py
```
To create indexes for the database.

You then need to set up ontologies correctly with:
```bash
docker exec beacon python beacon/db/extract_filtering_terms.py
docker exec beacon python beacon/db/get_descendants.py
```

To check if the user can query the `Beacon`, login to the Auth service and extract the token JWToken, then use it in a curl command like the following:
```bash
curl \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <JWToken>' \
  -X POST \
  -d '{
    "meta": {
        "apiVersion": "2.0"
    },
    "query": {
        "requestParameters": {
        "datasets": ["CINECA_synthetic_cohort_EUROPE_UK1"]       },
        "filters": [],
        "includeResultsetResponses": "HIT",
        "pagination": {
            "skip": 0,
            "limit": 10
        },
        "testMode": false,
        "requestedGranularity": "record"
    }
  }' \
https://beacon.gdi.nbis.se/api/individuals 
```

## Create endpoint for public crypt4gh key

From the VM where the storage-and-interfaces is deployed, extract the crypt4gh public key from the download container using:
```bash
docker cp download:/shared/c4gh.pub.pem .
```

Create a new bucket and upload the key to that bucket. Then change the key permissions to public:
```bash
s3cmd -c <s3config> mb s3://gdi-public
s3cmd -c <s3config> put c4gh.pub.pem s3://gdi-public/key/
s3cmd -c <s3config> setacl s3://gdi-public/key/c4gh.pub.pem --acl-public
```

In the Swedish case, the public key for the next step can be found under `https://s3.sto3.safedc.net/gdi-public/key/c4gh.pub.pem`

## Uploading data to the archive

Download the `c4gh.pub.pem` to the machine where the dataset exists.

Login to the auth endpoint (https://login.gdi.nbis.se) and download the s3config file containing the JWT token.
Download and extract the sda-cli
```bash
wget https://github.com/NBISweden/sda-cli/releases/download/v0.0.6/sda-cli_.0.0.6_Darwin_x86_64.tar.gz
tar -xvzf sda-cli_.0.0.6_Darwin_x86_64.tar.gz
```

Encrypt and upload the file using `sda-cli`
```bash
./sda-cli encrypt -key keys/c4gh.pub.pem <file_name>
./sda-cli upload -config s3cmd.conf <file_name>.c4gh (-targetDir <target_folder_location>)
```

To start the ingestion, use the `sda-admin` tool from the VM where the storage-and-interfaces product is deployed.
First, copy the `s3cmd.conf` file in the same folder as the `sda-admin` tool. Then check that the file uploaded earlier exists using
```bash
./sda-admin ingest
```
Then start the ingestion, create an accession ID and finally map the file to a dataset using
```bash
./sda-admin ingest <file_name_with_path>
./sda-admin accession <accession_id> <file_name_with_path>
./sda-admin dataset <dataset_id> <file_name_with_path>
```
For example:
```bash
./sda-admin ingest dir180523/file180523.test.c4gh
./sda-admin accession GDIF000000002 dir180523/file180523.test.c4gh
./sda-admin dataset GDID000000002  dir180523/file180523.test.c4gh
```

## Apply and get access to dataset
Login to REMS (deployed earlier), pick a dataset from the catalogue item list and apply for access. The handler then should approve the request and the user should now have the visas to access the files from the dataset.

## Deploying containerised computation
The `containerised-computation` product can be deployed by running
```bash
docker compose up --build -d
```
from the root of the repository. In the repository, there exists a job that calculates the md5sum of a file that exists in the archive. In order to run this job
1. Login with the LS AAI at the Auth service and get the JWToken
2. Edit the `examples/example-auth.sh` file and add the JWToken and the url to the file to be downloaded
3. Run
```bash
./examples/example-auth.sh
```
The result should be shown in the logs of the `containerised-computation` container. One example of the `examples-auth.sh` exists in the repo under `examples`.

## Get the files

### Get files with samtools
After getting the request for access approved, you should be able to download the files in the specified dataset. That can be achieved by:
1. Login to the auth service (deployed with storage-and-interface) (the url in the [SE case](https://login.gdi.nbis.se))
2. Copy the access token
3. Store the token in a file and export it to the `HTS_AUTH_LOCATION` variable
```bash
export HTS_AUTH_LOCATION=token.txt
```
4. Check the files that exist in the specific dataset using
```bash
curl --location \
    --header 'Authorization: Bearer <JWT_FROM_AUTH>' \
    'https://<DOWNLOAD_SERVICE_URL>/metadata/datasets/<DATASET_URL>/files'
```
e.g. for the Swedish case:
```bash
curl --location \
    --header 'Authorization: Bearer <JWT_FROM_AUTH>' \
    'https://download.gdi.nbis.se/metadata/datasets/https://gdi.nbis.se/datasets/gdi000000003/files'
```
5. Finally use samtools to download a file
```bash
samtools view <HTSGE_SERVICE_URL>/reads/s3/<DATASET_URL>/<FILE_URL_WITHOUT_C4GH>
```
e.g. for the Swedish case:
```bash
samtools view https://htsget.gdi.nbis.se/reads/s3/https://gdi.nbis.se/datasets/gdi000000003/c5773f41d17d27bd53b1e6794aedc32d7906e779_elixir-europe.org/gdi-heilsa/v9RYU2.sorted.bam
```
