# Build stage
# FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
# WORKDIR /app
# COPY . .
# RUN dotnet restore
# RUN dotnet publish -c Release -o out

# # Runtime stage (lightweight)
# FROM mcr.microsoft.com/dotnet/aspnet:8.0
# WORKDIR /app
# COPY --from=build /app/out .

# EXPOSE 8003

# CMD ["dotnet", "backend-dotnet.dll", "--urls", "http://0.0.0.0:8003"]


FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app

COPY backend-dotnet.csproj .
RUN dotnet restore

COPY . .
RUN dotnet publish -c Release -o out -p:PublishSingleFile=true

# ---------------- RUNTIME ----------------
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app

# ✅ Install curl HERE (not in build stage)
RUN apt-get update && apt-get install -y curl

COPY --from=build /app/out .

EXPOSE 8003

CMD ["./backend-dotnet", "--urls", "http://0.0.0.0:8003"]