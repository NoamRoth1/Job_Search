from src.networking.drafting import build_prompt_bundle, generate_variants
from src.networking.models import Contact, DraftRequest, VoiceProfile


def _request(**kwargs):
    contact = Contact(
        name="Grace Hopper",
        email="grace@example.com",
        company="Naval Research",
        role="Rear Admiral",
        notes="Presented at COBOL launch",
    )
    profile = VoiceProfile(name="Alex", role="Founder", tone="warm")
    payload = dict(
        contact=contact,
        goal="Compare notes on AI hiring",
        shared_context="Ada suggested we connect",
        highlight="drove a 35% uplift in pilot program",
        variant_count=2,
        time_options=["Wednesday 9am ET", "Thursday 1pm ET"],
        voice_profile=profile,
    )
    payload.update(kwargs)
    return DraftRequest(**payload)


def test_generate_variants_returns_requested_count():
    request = _request()
    drafts = generate_variants(request)
    assert len(drafts) == 2
    assert all("Wednesday" in draft.body for draft in drafts)


def test_build_prompt_bundle_contains_primer():
    request = _request()
    prompts = build_prompt_bundle(request)
    assert any("writes concise" in prompt for prompt in prompts)
    assert any("Contact:" in prompt for prompt in prompts)
