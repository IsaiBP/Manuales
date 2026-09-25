<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ $title ?? 'AIrNET' }}</title>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>
<body><main class="page-shell">{{ $slot }}</main></body>
</html>
