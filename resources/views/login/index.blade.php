<x-layouts.app title="Iniciar sesión | AIrNET">
    <x-auth-card title="Iniciar sesión" subtitle="Accede al centro de control de AIrNET.">
        @if(session('status')) <div class="alert success">{{ session('status') }}</div> @endif
        @if($errors->any()) <div class="alert error">{{ $errors->first() }}</div> @endif
        <form method="POST" action="{{ route('login.store') }}" class="form-stack">
            @csrf
            <label>Usuario o correo<input name="identifier" value="{{ old('identifier') }}" required autofocus></label>
            <label>Contraseña<input type="password" name="password" required></label>
            <label class="check"><input type="checkbox" name="remember" value="1"> Recordarme</label>
            <button type="submit">Iniciar sesión</button>
        </form>
        <p class="form-footer">¿No tienes cuenta? <a href="{{ route('register') }}">Crear cuenta</a></p>
    </x-auth-card>
</x-layouts.app>
