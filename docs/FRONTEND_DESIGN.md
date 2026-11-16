# Kabadiwala Connect — Frontend Design System
## Smart India Hackathon 2026

---

## 1. Brand Identity

**Product**: Kabadiwala Connect  
**Location**: Satara, India  
**Tagline**: YOUR SCRAP. A BETTER PRICE. A SMARTER JOURNEY.  
**Category**: Premium Climate-Tech × Circular Economy Marketplace  
**Tone**: Sophisticated, trustworthy, modern, Mumbai-meets-Silicon-Valley energy with deep Satara identity

---

## 2. Color System

### Base Palette
```css
--color-bg-primary:      #0d0f0e;   /* near-black — primary background */
--color-bg-secondary:    #111411;   /* dark forest — card backgrounds */
--color-bg-elevated:     #181c17;   /* elevated surfaces */
--color-bg-overlay:      rgba(13,15,14,0.85); /* modal/overlay */
```

### Text
```css
--color-text-primary:    #f0ede6;   /* warm off-white */
--color-text-secondary:  #a09d96;   /* stone — subtext */
--color-text-muted:      #6b6864;   /* muted — captions */
--color-text-accent:     #52a67a;   /* emerald accent text */
```

### Accent & Brand
```css
--color-accent:          #3d7a5f;   /* muted emerald — primary CTA */
--color-accent-light:    #52a67a;   /* lighter emerald — hover */
--color-accent-dim:      rgba(61,122,95,0.15); /* accent tint bg */
```

### Material Colors (used in 3D and data viz)
```css
--color-copper:          #b87333;   /* copper scrap */
--color-copper-light:    #d4956a;   /* highlight */
--color-aluminium:       #a8a8a8;   /* aluminium */
--color-steel:           #7a8c9e;   /* steel/iron */
--color-cardboard:       #c4a265;   /* cardboard */
--color-ewaste:          #5a7fa0;   /* e-waste blue */
--color-plastic:         #6b8fa5;   /* plastic */
```

### System Colors
```css
--color-border:          #222520;   /* subtle border */
--color-border-light:    #2d3229;   /* elevated border */
--color-amber:           #e8a22a;   /* warnings / pending */
--color-blue-muted:      #4a7fa0;   /* location / map */
--color-success:         #3d7a5f;   /* success state */
--color-error:           #a0443a;   /* error state */
```

---

## 3. Typography System

### Font Stack
```css
--font-display:   'Plus Jakarta Sans', sans-serif;
--font-body:      'Inter', sans-serif;
--font-mono:      'JetBrains Mono', monospace;
```

### Scale
| Token | Size | Weight | Use |
|---|---|---|---|
| `--text-hero` | clamp(3.5rem, 8vw, 8rem) | 800 | Hero headline |
| `--text-display` | clamp(2.5rem, 5vw, 5rem) | 800 | Section titles |
| `--text-h1` | clamp(2rem, 3.5vw, 3.5rem) | 700 | Page titles |
| `--text-h2` | clamp(1.5rem, 2.5vw, 2.5rem) | 700 | Section headings |
| `--text-h3` | 1.5rem | 600 | Card headings |
| `--text-body-lg` | 1.125rem | 400 | Lead paragraphs |
| `--text-body` | 1rem | 400 | Body text |
| `--text-small` | 0.875rem | 500 | Labels |
| `--text-caption` | 0.75rem | 500 | Captions, data |

### Letter Spacing
```css
--tracking-tight:    -0.03em;
--tracking-normal:   0em;
--tracking-wide:     0.05em;
--tracking-widest:   0.15em;  /* eyebrow labels */
```

---

## 4. Spacing System

```css
--space-1:   0.25rem;   /* 4px */
--space-2:   0.5rem;    /* 8px */
--space-3:   0.75rem;   /* 12px */
--space-4:   1rem;      /* 16px */
--space-6:   1.5rem;    /* 24px */
--space-8:   2rem;      /* 32px */
--space-10:  2.5rem;    /* 40px */
--space-12:  3rem;      /* 48px */
--space-16:  4rem;      /* 64px */
--space-20:  5rem;      /* 80px */
--space-24:  6rem;      /* 96px */
--space-32:  8rem;      /* 128px */
```

---

## 5. Component Architecture

### UI Components
- `Navbar` — minimal floating nav, blur on scroll
- `Footer` — dark, elegant
- `PrimaryButton` — emerald CTA
- `SecondaryButton` — ghost/outlined
- `SectionHeader` — eyebrow + title + subtitle
- `VerificationBadge` — authorized / verified / unverified
- `PriceCard` — material price display
- `MarketRange` — animated price range bar
- `OfferCard` — buyer/collector offer
- `CollectorCard` — collector profile
- `RecyclerCard` — recycler profile
- `Timeline` — traceability chain
- `PickupStatus` — real-time pickup state

### 3D Components
- `SataraScene` — main hero canvas
- `CameraRig` — scroll + mouse driven camera
- `ScrapObject` — individual material mesh
- `WeighingScale` — scale geometry
- `CollectorVehicle` — vehicle mesh
- `RecyclingJourney` — route line animation
- `CircularFlow` — final loop visualization
- `MaterialScanner` — sell page 3D scanner UI
- `PriceDisplay` — 3D price visualization

### Section Components
- `HeroSection` — full 3D immersive
- `ProblemSection` — fragmented → unified
- `HowItWorksSection` — 5-step journey
- `PriceIntelligenceSection` — interactive price discovery
- `SellScrapSection` — upload + AI identification
- `MarketplaceSection` — spatial offer cards
- `SmartPickupSection` — Satara map
- `VerificationSection` — badge system
- `TraceabilitySection` — timeline chain
- `BusinessSection` — bulk institutional
- `CollectorsSection` — informal collector empowerment
- `MarketMapSection` — dark Satara map
- `TrustSection` — transparency explanation
- `FinalTransformationSection` — circular loop CTA

---

## 6. Animation Hierarchy

### Priority 1 — Most Critical
- 3D hero camera choreography (scroll-driven)
- Scene transitions between major sections
- Material object interactions

### Priority 2 — High Value
- Section reveals (scroll-triggered)
- Price chart animations
- Route line drawing on map
- Timeline node animations

### Priority 3 — Polish
- Hover states on cards/buttons
- Text character stagger
- Number counting animations
- Badge pulse effects

### Priority 4 — Ambient
- Floating particles (max 300)
- Environmental glow
- Subtle object oscillation

---

## 7. 3D Design Rules

### What 3D Is For
- Storytelling: showing the physical journey of materials
- Immersion: making the experience feel like entering a real environment
- Emotional impact: premium brand perception

### What 3D Is NOT For
- Decoration without purpose
- Every section
- Operational UI (forms, tables, dashboards)

### Material Guidelines
```
MeshPhysicalMaterial for metals (copper, aluminium, steel)
  - metalness: 0.8–1.0
  - roughness: 0.2–0.5
  - envMapIntensity: 1.5–2.5

MeshStandardMaterial for non-metals (cardboard, plastic)
  - metalness: 0
  - roughness: 0.7–0.9
```

### Lighting Setup
```
AmbientLight: intensity 0.3, color warm white
DirectionalLight (key): intensity 1.2, from upper-right
DirectionalLight (fill): intensity 0.4, from lower-left  
HemisphereLight: sky #f0ede6, ground #111411, intensity 0.6
```

### Performance Budgets
| Device | Polygon budget | Particle limit | Postprocessing |
|---|---|---|---|
| Desktop 1440+ | 100k total | 500 | DepthOfField, SSAO |
| Laptop 1280 | 80k total | 300 | DepthOfField only |
| Tablet 768 | 50k total | 150 | None |
| Mobile 390 | 30k total | 0 | None |

---

## 8. Camera Behavior

### Hero Scroll Journey
| Scroll % | Camera Position | Focus Object |
|---|---|---|
| 0% | z=2.5, y=0.2 — macro | Copper wire |
| 0–20% | Pull back to z=5 | All materials |
| 20–40% | Shift right, z=7 | Weighing scale + price |
| 40–60% | Rise + rotate -15° | Collector vehicle |
| 60–80% | Wide pullback z=12 | Satara environment |
| 80–100% | Top-down + zoom out | Circular network |

### Mouse Parallax
- Horizontal mouse: ±5° camera Y rotation
- Vertical mouse: ±2° camera X rotation
- Speed: 0.05 lerp factor (very smooth)

---

## 9. Routes

| Path | Type | 3D Level |
|---|---|---|
| `/` | Full journey homepage | High — scroll 3D |
| `/sell` | Upload form + scanner | Medium — scanner UI |
| `/prices` | Price dashboard | Low — data viz |
| `/offers` | Marketplace | Low — card grid |
| `/pickup` | Pickup + map | Medium — Leaflet |
| `/track` | Status tracking | Low — timeline |
| `/recyclers` | Directory | Low — cards |
| `/collectors` | Network + dashboard | Low — cards |
| `/traceability` | Journey chain | Medium — timeline anim |
| `/business` | Bulk workflow | Low — forms |
| `/login` | Auth | None |

---

## 10. Responsive Strategy

### Desktop (1440px+)
- Full 3D hero, all effects
- 12-column grid
- Oversized typography

### Laptop (1280px)
- Reduced 3D complexity
- 12-column grid
- Slightly smaller typography

### Tablet (768px)
- Simplified 3D (no postprocessing)
- 8-column grid
- Stacked layouts where needed

### Mobile (390px)
- Static scene or very simple 3D
- Single column
- All core flows preserved
- Hamburger nav

---

## 11. Accessibility

```
- All interactive elements keyboard-navigable
- Focus rings: 2px emerald outline
- ARIA labels on all buttons/inputs
- Color contrast ≥ 4.5:1 for body text
- prefers-reduced-motion → disable camera movement, parallax, particles
- Screen reader fallbacks for 3D content
```

---

## 12. Performance Rules

1. Lazy-load all route components
2. Suspend 3D canvas until visible
3. Use `draco` compression for any GLB assets
4. Limit draw calls per frame < 50
5. Use `instancedMesh` for repeated geometry
6. Debounce scroll handlers
7. Use `useFrame` selectively — only active objects
8. Target 60fps on M1 MacBook Air / mid-range Windows laptop
