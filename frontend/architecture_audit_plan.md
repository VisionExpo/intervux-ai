# Intervux AI: Frontend Architecture & UI Modernization Plan

This document outlines the architectural roadmap to migrate the Intervux AI frontend from a fragmented Tailwind/global-CSS structure to a modular, glossy, premium dark-mode design system utilizing Vanilla CSS Modules and Framer Motion.

## User Review Required
> [!WARNING]
> This migration involves removing the legacy `App.css` completely and stripping out Tailwind usage to embrace strict Vanilla CSS Modules. Phase 1 will temporarily break the UI of internal dashboard pages until Phase 3 rebuilds them with the new modular primitives. Please confirm if this temporary visual regression in local development is acceptable during the migration phases.

## Proposed Changes
The entire design language is moving toward a **Deep Ocean Blue to Indigo** aesthetic. We will purge Tailwind in favor of strongly-typed CSS tokens and modular component stylesheets. 

---

### Codebase Audit Summary
Current codebase is highly fragmented. React components (`Sidebar.tsx`, `App.tsx`) mix inline Tailwind classes, vanilla CSS imports (`App.css`), and localized CSS Modules (`Auth.module.css`). There is duplication of layout logic (e.g., standalone `Sidebar.tsx` vs. `EnterpriseAppLayout.tsx`). The layout architecture relies heavily on monolithic CSS in `App.css` (over 1700 lines), defining global scoped classes for specific pages (`.login-page`, `.dashboard-shell`), leading to poor modularity, duplicated logic, and brittle component encapsulation.

### UI Architecture Risks
1. **CSS Specificity Collisions**: Global classes in `App.css` (`.panel`, `.candidate-card`, `.stat-card`) run a high risk of conflicting with future module-based styles.
2. **Styling Fragmentation**: Combining Tailwind, CSS Modules, and monolithic pure CSS means there is no single source of truth for the design system. 
3. **Hardcoded Theming**: Hex values (`#1a2940`, `#c84630`, `#3b82f6`) are hardcoded across `.css` and `.module.css` files rather than securely bound to CSS variables.
4. **Duplicate Layout Logic**: The existence of both `EnterpriseAppLayout.tsx` and `Sidebar.tsx` indicates overlapping responsibilities and disjointed navigation logic.

### Refactor Opportunities
1. Clean up duplicate layouts, abstracting navigation into a single `AppShell` relying on a robust `<Sidebar />` layout component primitive.
2. Replace monolithic `App.css` DOM structures with a standalone `<GlassCard>` component (`components/ui/GlassCard/GlassCard.tsx`) paired with its own CSS module.
3. Centralize typography, spacing, and glass effects into a root `tokens.css`.
4. Refactor `Login.tsx` and `Signup.tsx` to utilize a shared `<AuthSurface>` component rather than reinventing gradient containers.
5. Abstract shared dashboard UI metrics into a `<MetricTile>` component utilizing Framer Motion for initial entrance animations.

### Design System Proposal
We will implement a modular, token-first architecture built on Vanilla CSS Modules without the dependency of Tailwind utilities.

```text
src/
  styles/
    tokens.css       (Global colors: Deep Ocean/Indigo, Spacing, Shadows, Blur scales)
    globals.css      (CSS reset, root body definitions, typography definitions)
    motion.css       (Standard cubic-bezier transition constants)

  components/
    ui/              (Dumb UI primitives)
      Button/
      GlassCard/
      Input/
      Modal/
    layout/          (Smart layout framework)
      Sidebar/
      TopHeader/
      PageShell/

  layouts/
    EnterpriseLayout/ (The main authenticated routing shell)

  pages/             (Feature domains)
    Auth/
    Dashboard/
```

**Proposed Core Tokens (`tokens.css`):**
- `--bg-ocean-base`: `#090f1b;`
- `--bg-ocean-elevated`: `#0d1526;`
- `--surface-glass-light`: `rgba(255, 255, 255, 0.03);`
- `--surface-glass-heavy`: `rgba(255, 255, 255, 0.08);`
- `--border-glass`: `rgba(255, 255, 255, 0.06);`
- `--border-glass-glow`: `rgba(79, 70, 229, 0.3);`
- `--accent-indigo`: `#4f46e5;`
- `--accent-ocean`: `#0ea5e9;`
- `--blur-sm`: `blur(4px);`
- `--blur-md`: `blur(12px);`
- `--blur-lg`: `blur(24px);`

### File-by-File Migration Plan
1. **`src/index.css`** 
   - Remove Tailwind directives. Import `tokens.css` and `globals.css` instead. Set strict dark mode root body styles.
2. **`src/App.css`** 
   - Delete entirely. Distribute its sprawling rules into dedicated UI component CSS modules (e.g. `GlassCard.module.css`, `Button.module.css`).
3. **`src/components/Sidebar.tsx`** 
   - Migrate inline Tailwind classes to `Sidebar.module.css` utilizing `tokens.css` variables. Move to `components/layout/Sidebar/`.
4. **`src/layouts/EnterpriseAppLayout.tsx`**
   - Streamline the layout logic. Swap any remaining legacy icons for `lucide-react`. Integrate Framer Motion for the layout wrapper.
5. **`src/pages/Login.tsx` & `src/pages/Signup.tsx`**
   - Remove `Auth.module.css` local backgrounds. Inject the `<AuthSurface>` layout component with standard glossy dark styling to ensure complete auth consistency.

### Phased Execution Roadmap

#### Phase 1: Core Design System + Layout Shell
- Setup `styles/tokens.css`, `globals.css`.
- Delete `App.css` and strip out Tailwind dependencies.
- Rebuild `EnterpriseAppLayout` utilizing Modular CSS and the Ocean Blue/Indigo token palette.
- **Risk Level**: High (Breaks legacy pages immediately). **Effort**: High.
- **Testing Checklist**: Verify CSS resets, token parsing, and layout shell responsiveness on desktop & mobile.

#### Phase 2: Authentication & Dashboard Primitives
- Build foundation primitives: `<GlassCard>`, `<Button>`, `<Input>`, `<AuthSurface>`.
- Refactor `Login.tsx` and `Signup.tsx` to strictly use the new primitives.
- **Risk Level**: Low. **Effort**: Medium.
- **Testing Checklist**: Verify auth flows, form validation states, and responsive stacking on auth surfaces.

#### Phase 3: Feature Pages & Workflows
- Abstract layout metrics and tables out of `CandidateDashboard.tsx`, `RecruiterDashboard.tsx`, and `AdminDashboard.tsx`.
- Rebuild stat charts, applicant tables, and intelligence workflows into standalone dynamic components.
- **Risk Level**: Medium. **Effort**: High.
- **Testing Checklist**: Verify data fetching integration, table scrolling, and glass modal behaviors.

#### Phase 4: Animations, Responsiveness & Polish
- Integrate `<AnimatePresence>` and Framer Motion orchestrations for page transitions and data load staggers.
- Add hover micro-interactions, active state glows, and finalize responsive tuning for all devices.
- **Risk Level**: Low. **Effort**: Medium.
- **Testing Checklist**: Profile animation paint frames, ensure smooth 60fps renders, and audit mobile device views.

### Performance / Maintainability Risks
- **Performance**: High utilization of `backdrop-filter: blur()` can cause significant rendering bottlenecks on lower-end devices or Safari. We must standardize to realistic blur levels (e.g., 8px-12px) and utilize safe rendering composite hacks (`will-change: transform, backdrop-filter; translateZ(0)`) to lock hardware acceleration.
- **Maintainability**: Moving from Tailwind to CSS Modules requires immense discipline. Developers must explicitly rely on `var(--tokens)` for any colors, spacing, or blurs and never inject hardcoded single-use HEX values or margin px overrides in local `.module.css` files, otherwise styling fragmentation will quickly resurface.

### Final Recommendation
Proceed immediately starting with **Phase 1** to cleanly sever the legacy monolithic `App.css` dependency. By forcing the platform into strict Vanilla CSS Modules rooted in a single `tokens.css`, the application will naturally adopt the "Premium Glossy Deep Ocean" aesthetic seamlessly. The layout should be migrated first to establish the container shell, followed by a targeted structural pass over the Authentication flow and Dashboard grids.

## Open Questions
- Do you want to preserve any of the existing red/warm color accents from the legacy application (`#c84630`), or should we fully replace everything with the Ocean Blue/Indigo spec?
- Shall we completely uninstall `tailwindcss`, `postcss`, and `autoprefixer` dependencies in Phase 1 to enforce strict Vanilla CSS Module rules?

## Verification Plan
1. **Automated Tests**: Basic route validation tests will ensure no module parsing errors crash the React application during migration.
2. **Visual Audits**: We will manually inspect the Layout shell, login flow, and a sample dashboard grid, capturing screenshots to ensure glassmorphism blur and shadow tokens meet the expected premium criteria.
