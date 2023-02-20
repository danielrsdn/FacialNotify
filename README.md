# FacialNotify
Back-end microservice that leverages deep learning libraries to perform facial feature detection on images, and notifies a recipient via SMS. This service is listening to a queue on AWS SQS for messages containing recipients and image names. It downloads the image from AWS S3 Storage and performs facial feature detection on individuals detected in the images. It uses AWS SNS to send a text message to the recipient(s) informing them of the physical features detected.

## Requirements
  * [python3][python] 3.8+
  * [pip3][pip] 23.0+


[python]: https://www.python.org/downloads/
[pip]: https://pypi.org/project/pip/

## Run 

Start service by running:

```bash
$ python3 src/app.py
```
