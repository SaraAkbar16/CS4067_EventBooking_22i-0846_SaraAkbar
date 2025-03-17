# Use official Nginx image
FROM nginx:latest

# Remove the default Nginx HTML files
RUN rm -rf /usr/share/nginx/html/*

# Copy the HTML files into the Nginx default directory
COPY . /usr/share/nginx/html/

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
