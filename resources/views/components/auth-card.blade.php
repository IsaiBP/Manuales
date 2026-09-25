@props(['title', 'subtitle' => null])
<section class="auth-card">
    <div class="brand-mark">AIr<span>NET</span></div>
    <h1>{{ $title }}</h1>
    @if($subtitle)<p class="muted">{{ $subtitle }}</p>@endif
    {{ $slot }}
</section>
