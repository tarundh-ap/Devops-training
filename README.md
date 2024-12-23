# Devops-training
- I ran a bootstrap based template using the official Docker Nginx Image.
- I learned to mount the directory so the nginx could serve them
- Made a dockerfile to automate the process of building an image which includes the bootstrap template directly so we don't need to mount the template files each time we run the container.


- TO BUILD THE IMAGE:
  -  Open the terminal from the directory where the dockerfile is.
  -  In terminal run the command '''docker build --tag image-name:latest .'''
