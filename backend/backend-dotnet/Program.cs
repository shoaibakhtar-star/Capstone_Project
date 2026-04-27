using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using System.Text;
using MySqlConnector;
using Dapper;
using DotNetEnv;

using System;
using System.Linq;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;

Env.Load(); // load .env

var builder = WebApplication.CreateBuilder(args);

// ---------------- CONFIG ----------------
var SECRET_KEY = Environment.GetEnvironmentVariable("SECRET_KEY") ?? "default_secret";
var connectionString = $"server={Environment.GetEnvironmentVariable("DB_HOST")};" +
                       $"user={Environment.GetEnvironmentVariable("DB_USER")};" +
                       $"password={Environment.GetEnvironmentVariable("DB_PASSWORD")};" +
                       $"database={Environment.GetEnvironmentVariable("DB_NAME")}";

// ---------------- SERVICES ----------------
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddAuthorization(); // ✅ ADD THIS

// JWT
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddAuthorization();

builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
})
.AddJwtBearer(options =>
{
    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuer = false,
        ValidateAudience = false,
        ValidateLifetime = true,
        ValidateIssuerSigningKey = true,
        IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(SECRET_KEY))
    };
});

builder.Logging.ClearProviders();
builder.Logging.AddConsole();


builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", policy =>
    {
        policy
            .AllowAnyOrigin()
            .AllowAnyMethod()
            .AllowAnyHeader();
    });
});

var app = builder.Build();

app.UseCors("AllowAll");

app.Use(async (context, next) =>
{
    var logger = context.RequestServices.GetRequiredService<ILoggerFactory>()
                                        .CreateLogger("RequestLogger");

    var start = DateTime.UtcNow;

    logger.LogInformation("Incoming Request: {method} {url}",
        context.Request.Method,
        context.Request.Path);

    await next();

    var duration = DateTime.UtcNow - start;

    logger.LogInformation("Response: {statusCode} in {duration} ms",
        context.Response.StatusCode,
        duration.TotalMilliseconds);
});


app.UseExceptionHandler(errorApp =>
{
    errorApp.Run(async context =>
    {
        var logger = context.RequestServices.GetRequiredService<ILoggerFactory>()
                                            .CreateLogger("GlobalException");

        var exception = context.Features.Get<Microsoft.AspNetCore.Diagnostics.IExceptionHandlerFeature>()?.Error;

        if (exception != null)
        {
            logger.LogError(exception, "Unhandled exception occurred");
        }

        context.Response.StatusCode = 500;
        await context.Response.WriteAsJsonAsync(new { error = "Internal Server Error" });
    });
});

app.UseAuthentication();
app.UseAuthorization();

// ---------------- ROUTES ----------------

// Health
app.MapGet("/health", async () =>
{
    try
    {
        using var db = new MySqlConnection(connectionString);
        await db.OpenAsync();
        return Results.Ok(new { status = "healthy dotnet" });
    }
    catch (Exception ex)
    {
        Console.WriteLine($"DB Connection Failed. ConnStr: {connectionString} | Error: {ex.Message}");
        return Results.Json(new { status = "unhealthy dotnet", error = ex.Message }, statusCode: 503);
    }
});

// Register
app.MapPost("/auth/register", async (User user) =>
{
    using var db = new MySqlConnection(connectionString);

    try
    {
        await db.ExecuteAsync(
            "INSERT INTO users (username, password) VALUES (@Username, @Password)",
            new { Username = user.Username, Password = user.Password }
        );

        return Results.Ok(new { message = "User registered" });
    }
    catch
    {
        return Results.BadRequest(new { detail = "User already exists" });
    }
});

// Login
app.MapPost("/auth/login", async (User user) =>
{
    using var db = new MySqlConnection(connectionString);

    var result = await db.QueryFirstOrDefaultAsync<dynamic>(
        "SELECT id, password FROM users WHERE username = @Username",
        new { Username = user.Username }
    );

    if (result == null)
        return Results.Unauthorized();

    if (user.Password != result.password)
        return Results.Unauthorized();

    var token = CreateToken((int)result.id, SECRET_KEY);

    return Results.Ok(new { access_token = token });
});

// Profile (Protected)
app.MapGet("/auth/profile", (HttpContext context) =>
{
    var userId = context.User.Claims.FirstOrDefault(c => c.Type == "user_id")?.Value;

    if (userId == null)
        return Results.Unauthorized();

    return Results.Ok(new { user_id = userId });
}).RequireAuthorization();

app.Run("http://0.0.0.0:8003");


// ---------------- TOKEN FUNCTION ----------------
string CreateToken(int userId, string secret)
{
    var handler = new System.IdentityModel.Tokens.Jwt.JwtSecurityTokenHandler();
    var key = Encoding.UTF8.GetBytes(secret);

    var descriptor = new SecurityTokenDescriptor
    {
        Subject = new System.Security.Claims.ClaimsIdentity(new[]
        {
            new System.Security.Claims.Claim("user_id", userId.ToString())
        }),
        Expires = DateTime.UtcNow.AddMinutes(30),
        SigningCredentials = new SigningCredentials(
            new SymmetricSecurityKey(key),
            SecurityAlgorithms.HmacSha256
        )
    };

    var token = handler.CreateToken(descriptor);
    return handler.WriteToken(token);
}