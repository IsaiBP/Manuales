<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\Rules\Password;
use Illuminate\View\View;

class AuthController extends Controller
{
    public function showLogin(): View { return view('login.index'); }

    public function showRegister(): View { return view('login.register'); }

    public function login(Request $request): RedirectResponse
    {
        $data = $request->validate([
            'identifier' => ['required', 'string'],
            'password' => ['required', 'string'],
        ], [
            'identifier.required' => 'Escribe tu usuario o correo.',
            'password.required' => 'Escribe tu contraseña.',
        ]);

        $identifier = strtolower(trim($data['identifier']));
        $user = User::query()
            ->where(fn ($query) => $query
                ->where('email', $identifier)
                ->orWhere('username', $identifier))
            ->first();

        $valid = $user && $user->active && Hash::check($data['password'], $user->password);

        if (! $valid) {
            return back()->withInput()->withErrors([
                'identifier' => 'Las credenciales no son válidas o la cuenta está inactiva.',
            ]);
        }

        Auth::login($user, $request->boolean('remember'));
        $request->session()->regenerate();

        return redirect()->intended(route('dashboard'));
    }

    public function register(Request $request): RedirectResponse
    {
        $data = $request->validate([
            'name' => ['required', 'string', 'max:120'],
            'username' => ['required', 'string', 'alpha_dash', 'min:3', 'max:40', 'unique:users,username'],
            'email' => ['required', 'string', 'email', 'max:120', 'unique:users,email'],
            'password' => [
                'required',
                'confirmed',
                Password::min(6)->mixedCase()->numbers()->symbols(),
            ],
        ], ['password.confirmed' => 'Las contraseñas deben coincidir.']);

        User::create([
            'name' => $data['name'],
            'username' => strtolower($data['username']),
            'email' => strtolower($data['email']),
            'password' => $data['password'],
            'role' => 'USER',
            'active' => true,
        ]);

        return redirect()->route('login')->with('status', 'Cuenta creada. Ya puedes iniciar sesión.');
    }

    public function logout(Request $request): RedirectResponse
    {
        Auth::logout();
        $request->session()->invalidate();
        $request->session()->regenerateToken();

        return redirect()->route('login');
    }
}
