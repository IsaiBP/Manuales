<x-layouts.app title="Crear cuenta | AIrNET">
    <x-auth-card title="Crear cuenta" subtitle="Registra un usuario para comenzar.">
        @if($errors->any()) <div class="alert error">{{ $errors->first() }}</div> @endif
        <form method="POST" action="{{ route('register.store') }}" class="form-stack">
            @csrf
            <label>Nombre completo<input name="name" value="{{ old('name') }}" required></label>
            <label>Nombre de usuario<input name="username" value="{{ old('username') }}" required></label>
            <label>Correo electrónico<input type="email" name="email" value="{{ old('email') }}" required></label>
            <label>Contraseña<input type="password" name="password" required></label>
            <label>Confirmar contraseña<input type="password" name="password_confirmation" required></label>
            <p class="hint">Mínimo 6 caracteres, una mayúscula, un número y un símbolo.</p>
            <button type="submit">Crear cuenta</button>
        </form>
        <p class="form-footer">¿Ya tienes cuenta? <a href="{{ route('login') }}">Iniciar sesión</a></p>
    </x-auth-card>
</x-layouts.app>
