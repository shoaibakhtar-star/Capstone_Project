FROM mcr.microsoft.com/dotnet/sdk:8.0

WORKDIR /app

# Copy all project files
COPY . .

# Restore dependencies
RUN dotnet restore

# Publish the app
RUN dotnet publish -c Release -o out

# Move to published folder
WORKDIR /app/out

# Expose port
EXPOSE 8003

# Run compiled app
CMD ["dotnet", "backend-dotnet.dll", "--urls", "http://0.0.0.0:8003"]