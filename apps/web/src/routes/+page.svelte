<script lang="ts">
  import { onMount } from 'svelte';

  onMount(async () => {
    // Check user preference for reduced motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return;

    try {
      const animeModule = (await import('animejs')) as unknown as {
        default?: (params: unknown) => void;
      };
      const anime = animeModule.default || (animeModule as unknown as (params: unknown) => void);
      if (typeof anime === 'function') {
        anime({
          targets: '.animate-fade-in',
          opacity: [0, 1],
          translateY: [16, 0],
          delay: (el: unknown, i: number) => i * 120,
          duration: 700,
          easing: 'easeOutQuad',
        });
      }
    } catch {
      // Fallback: Elements default to visible via CSS
    }
  });
</script>

<div class="landing-page flex flex-col gap-24 py-8 sm:py-16">
  <!-- Hero Section -->
  <section class="hero text-center max-w-3xl mx-auto px-4 flex flex-col items-center gap-6">
    <div
      class="animate-fade-in inline-flex items-center gap-2 px-3 py-1 rounded-full border border-[var(--hairline)] bg-[var(--graphite)] text-xs text-[var(--chalk)]"
    >
      <span class="h-2 w-2 rounded-full bg-[var(--mint)] animate-pulse"></span>
      <span>Autonomous Job Hunting with Human-in-the-Loop</span>
    </div>

    <h1
      class="animate-fade-in text-4xl sm:text-6xl font-normal tracking-tight text-[var(--snow)] leading-tight"
    >
      Find jobs faster.<br />
      <span class="text-[var(--arc-blue)]">Apply with confidence.</span>
    </h1>

    <p class="animate-fade-in text-base sm:text-lg text-[var(--fog)] max-w-2xl leading-relaxed">
      Vanguard discovers live job listings, matches your profile using Gemini AI, and fills
      application forms in a real browser. It pauses at the finish line so you approve every single
      submission.
    </p>

    <div class="animate-fade-in flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto mt-2">
      <a
        href="/login?mode=signup"
        class="btn btn-primary w-full sm:w-auto px-8 py-3 bg-[var(--bone)] text-[var(--ink)] hover:bg-white rounded-xl font-medium text-base shadow-lg transition-transform hover:-translate-y-0.5"
      >
        Get started free
      </a>
      <a
        href="/login"
        class="btn btn-secondary w-full sm:w-auto px-8 py-3 bg-[var(--charcoal)] text-[var(--snow)] hover:bg-[var(--smoke)] border border-[var(--hairline)] rounded-xl font-medium text-base transition-colors"
      >
        Sign in to dashboard
      </a>
    </div>

    <!-- Live Preview Mockup Card -->
    <div
      class="animate-fade-in w-full mt-8 p-4 sm:p-6 bg-[var(--graphite)] border border-[var(--hairline)] rounded-2xl shadow-2xl text-left"
    >
      <div class="flex items-center justify-between pb-3 border-b border-[var(--hairline)] mb-4">
        <div class="flex items-center gap-2">
          <span class="h-3 w-3 rounded-full bg-red-500/80"></span>
          <span class="h-3 w-3 rounded-full bg-yellow-500/80"></span>
          <span class="h-3 w-3 rounded-full bg-green-500/80"></span>
          <span class="ml-2 font-mono text-xs text-[var(--steel)]"
            >vanguard-agent :: session running</span
          >
        </div>
        <span
          class="badge badge-sm border-none bg-amber-400/20 text-amber-300 font-mono text-[10px]"
        >
          WAITING_FOR_USER
        </span>
      </div>
      <div class="space-y-3 font-mono text-xs text-[var(--chalk)]">
        <p class="text-[var(--fog)]">
          > Discovering vacancies for query "Staff Software Engineer remote"...
        </p>
        <p class="text-[var(--mint)]">
          > Found 14 matching opportunities on company careers pages.
        </p>
        <p class="text-[var(--arc-blue)]">
          > Opening browser automation session with Playwright...
        </p>
        <p class="text-[var(--chalk)]">
          > Application form pre-filled: Name, Resume, Portfolio, Experience.
        </p>
        <div class="p-3 bg-[var(--void)] rounded-lg border border-[var(--hairline)] mt-3">
          <p class="text-amber-400 font-medium mb-1">Gate triggered: ready_to_submit</p>
          <p class="text-[var(--steel)] text-[11px]">
            Submission stopped. Vanguard will never click "Submit" without your explicit approval.
          </p>
        </div>
      </div>
    </div>
  </section>

  <!-- Safety & Human-in-the-Loop Section -->
  <section class="safety-banner max-w-5xl mx-auto px-4 w-full">
    <div
      class="p-8 rounded-2xl bg-gradient-to-b from-[var(--graphite)] to-[var(--charcoal)] border border-[var(--hairline)] flex flex-col md:flex-row items-center gap-8"
    >
      <div
        class="h-16 w-16 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center shrink-0"
      >
        <svg class="h-8 w-8 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
          />
        </svg>
      </div>
      <div>
        <h2 class="text-2xl font-normal text-[var(--snow)] mb-2">
          Strict Human-in-the-Loop Guarantee
        </h2>
        <p class="text-sm text-[var(--fog)] leading-relaxed">
          Autonomous agents shouldn't spam employers or send unchecked information. Vanguard fills
          forms, captures screenshots of every step, and pauses before the final submission. You
          retain complete authority over every job application.
        </p>
      </div>
    </div>
  </section>

  <!-- 4-Step Workflow -->
  <section class="workflow max-w-5xl mx-auto px-4 w-full">
    <div class="text-center mb-12">
      <h2 class="text-3xl font-normal text-[var(--snow)] mb-3">How Vanguard Works</h2>
      <p class="text-sm text-[var(--fog)] max-w-lg mx-auto">
        Four transparent steps from listing discovery to validated application.
      </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div
        class="card p-6 bg-[var(--graphite)] border border-[var(--hairline)] rounded-xl space-y-3"
      >
        <span class="font-mono text-xs text-[var(--arc-blue)] font-bold">01 / DISCOVERY</span>
        <h3 class="text-base font-medium text-[var(--snow)]">Live Web Search</h3>
        <p class="text-xs text-[var(--fog)] leading-relaxed">
          Searches public job postings and company boards. Never fabricates listings or salaries.
        </p>
      </div>

      <div
        class="card p-6 bg-[var(--graphite)] border border-[var(--hairline)] rounded-xl space-y-3"
      >
        <span class="font-mono text-xs text-[var(--arc-blue)] font-bold">02 / MATCHING</span>
        <h3 class="text-base font-medium text-[var(--snow)]">AI Profile Extraction</h3>
        <p class="text-xs text-[var(--fog)] leading-relaxed">
          Parses your resume PDF with Gemini AI, organizing your skills and work history into
          structured records.
        </p>
      </div>

      <div
        class="card p-6 bg-[var(--graphite)] border border-[var(--hairline)] rounded-xl space-y-3"
      >
        <span class="font-mono text-xs text-[var(--arc-blue)] font-bold">03 / AUTOMATION</span>
        <h3 class="text-base font-medium text-[var(--snow)]">Browser Form Fill</h3>
        <p class="text-xs text-[var(--fog)] leading-relaxed">
          Playwright navigates to application forms, populating fields accurately without bypassing
          CAPTCHAs.
        </p>
      </div>

      <div
        class="card p-6 bg-[var(--graphite)] border border-[var(--hairline)] rounded-xl space-y-3"
      >
        <span class="font-mono text-xs text-[var(--mint)] font-bold">04 / APPROVAL</span>
        <h3 class="text-base font-medium text-[var(--snow)]">Your Decision</h3>
        <p class="text-xs text-[var(--fog)] leading-relaxed">
          Inspect what was filled and click Approve to finalize the submission.
        </p>
      </div>
    </div>
  </section>

  <!-- Features Grid -->
  <section class="features max-w-5xl mx-auto px-4 w-full">
    <div class="text-center mb-12">
      <h2 class="text-3xl font-normal text-[var(--snow)] mb-3">Enterprise-Grade Architecture</h2>
      <p class="text-sm text-[var(--fog)] max-w-lg mx-auto">
        Built for speed, reliability, and utmost security.
      </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="p-6 bg-[var(--graphite)] border border-[var(--hairline)] rounded-xl space-y-3">
        <h3 class="text-base font-medium text-[var(--snow)]">Supabase Auth & Storage</h3>
        <p class="text-xs text-[var(--fog)] leading-relaxed">
          Secure authentication with Google OAuth or email/password. Resumes stored in private
          buckets with short-lived signed URLs.
        </p>
      </div>

      <div class="p-6 bg-[var(--graphite)] border border-[var(--hairline)] rounded-xl space-y-3">
        <h3 class="text-base font-medium text-[var(--snow)]">Atomic Task Queue</h3>
        <p class="text-xs text-[var(--fog)] leading-relaxed">
          PostgreSQL-backed worker tasks with <code>SKIP LOCKED</code> semantics, guaranteeing zero dropped
          or duplicated applications.
        </p>
      </div>

      <div class="p-6 bg-[var(--graphite)] border border-[var(--hairline)] rounded-xl space-y-3">
        <h3 class="text-base font-medium text-[var(--snow)]">Privacy by Design</h3>
        <p class="text-xs text-[var(--fog)] leading-relaxed">
          Row Level Security ensures your data is only ever accessible to your account. No telemetry
          tracking or credential logging.
        </p>
      </div>
    </div>
  </section>

  <!-- Call to action footer banner -->
  <section class="cta-banner max-w-3xl mx-auto px-4 text-center space-y-6">
    <h2 class="text-3xl font-normal text-[var(--snow)]">Ready to streamline your job hunt?</h2>
    <p class="text-sm text-[var(--fog)]">
      Set up your profile, upload your resume, and let Vanguard handle the repetitive busywork.
    </p>
    <a
      href="/login?mode=signup"
      class="btn btn-primary px-8 py-3 bg-[var(--bone)] text-[var(--ink)] hover:bg-white rounded-xl font-medium text-base inline-block"
    >
      Create your account
    </a>
  </section>

  <!-- Footer -->
  <footer
    class="border-t border-[var(--hairline)] pt-8 pb-12 text-center text-xs text-[var(--steel)]"
  >
    <div class="flex items-center justify-center gap-6 mb-4">
      <a href="/login" class="hover:text-[var(--snow)] transition-colors">Sign in</a>
      <a href="/login?mode=signup" class="hover:text-[var(--snow)] transition-colors">Register</a>
      <a
        href="https://github.com/RizkiRdm/vanguard-job-hunting"
        target="_blank"
        rel="noreferrer"
        class="hover:text-[var(--snow)] transition-colors">GitHub</a
      >
    </div>
    <p>
      &copy; {new Date().getFullYear()} Vanguard. Open-source autonomous job discovery assistant.
    </p>
  </footer>
</div>
