<x-layouts.app title="Dashboard | AIrNET">
    <section class="dashboard-card">
        <div class="dashboard-header">
            <div><div class="brand-mark">AIr<span>NET</span></div><p class="muted">Centro de control</p></div>
            <form method="POST" action="{{ route('logout') }}">@csrf<button class="button-ghost">Cerrar sesión</button></form>
        </div>
        <div class="welcome"><p class="eyebrow">Panel de usuario</p><h1>Bienvenido, {{ auth()->user()->name }}</h1><p class="muted">Tu sesión está activa y tu cuenta está habilitada.</p></div>
        <div class="dashboard-grid">
            <div class="metric"><span>Dispositivos vinculados</span><strong>0</strong></div>
            <div class="metric"><span>Alertas pendientes</span><strong>0</strong></div>
            <div class="metric"><span>Estado de cuenta</span><strong class="active-text">Activa</strong></div>
        </div>
    </section>
</x-layouts.app>
