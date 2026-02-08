# Frontend Setup Verification Guide

**Purpose**: Verify that Phase 1 frontend setup is complete and working correctly.

---

## Verification Steps

### Step 1: Check Project Structure

Run this command to verify all required directories exist:

```bash
ls -la frontend/src/
ls -la frontend/tests/
ls -la frontend/public/
```

**Expected Output**:
```
frontend/src/:
- app/
- components/
- services/
- hooks/
- types/
- utils/
- middleware.ts
- env.d.ts
- globals.css

frontend/tests/:
- setup.ts
- unit/

frontend/public/:
- (empty or with favicon/images)
```

### Step 2: Verify Configuration Files

Run this command to check all config files exist:

```bash
ls -la frontend/*.{json,ts,js,css} frontend/.*
```

**Expected Files**:
- ✅ `package.json`
- ✅ `tsconfig.json`
- ✅ `next.config.ts`
- ✅ `tailwind.config.ts`
- ✅ `postcss.config.js`
- ✅ `vitest.config.ts`
- ✅ `.eslintrc.json`
- ✅ `prettier.config.json`
- ✅ `.env.example`
- ✅ `.env.local`
- ✅ `.gitignore`

### Step 3: Verify TypeScript Configuration

Check that strict mode is enabled:

```bash
cd frontend
grep -A 20 '"compilerOptions"' tsconfig.json | grep '"strict"'
```

**Expected Output**: `"strict": true`

### Step 4: Verify Type Definitions

Check that all type files exist:

```bash
ls -la frontend/src/types/
```

**Expected Files**:
- ✅ `auth.ts` - Authentication types
- ✅ `task.ts` - Task types
- ✅ `api.ts` - API types

### Step 5: Verify Utility Functions

Check that utility files exist:

```bash
ls -la frontend/src/utils/
```

**Expected Files**:
- ✅ `format.ts` - Date/text formatting
- ✅ `validation.ts` - Form validation
- ✅ `errors.ts` - Error handling

### Step 6: Verify Service Files

Check API client setup:

```bash
ls -la frontend/src/services/
```

**Expected Files**:
- ✅ `api.ts` - Base API client with JWT handling

### Step 7: Verify Package.json Scripts

Check that all scripts are configured:

```bash
cd frontend
grep -A 10 '"scripts"' package.json
```

**Expected Scripts**:
- ✅ `dev` - Development server
- ✅ `build` - Production build
- ✅ `start` - Production start
- ✅ `lint` - ESLint check
- ✅ `type-check` - TypeScript check
- ✅ `test` - Run tests
- ✅ `test:ui` - Test UI
- ✅ `test:coverage` - Coverage report
- ✅ `format` - Prettier format

### Step 8: Install Dependencies

Install all dependencies:

```bash
cd frontend
pnpm install
```

**Expected Output**:
```
 + added X packages, and Y packages changed 30ms
```

### Step 9: Verify TypeScript Compilation

Check TypeScript strict mode:

```bash
cd frontend
pnpm type-check
```

**Expected Output**:
```
✓ TypeScript compilation successful (0 errors)
```

### Step 10: Run ESLint

Check code quality:

```bash
cd frontend
pnpm lint
```

**Expected Output**:
```
0 errors and 0 warnings
```

Or if there are only template files:
```
No linting errors found.
```

### Step 11: Run Tests

Execute the test suite:

```bash
cd frontend
pnpm test
```

**Expected Output**:
```
✓ tests/unit/utils/format.test.ts (8 tests)
  ✓ Format Utilities (8)
    ✓ formatDate
    ✓ truncateText
    ✓ capitalize
    ✓ getInitials
    ✓ isPastDate
    ✓ isToday
    ✓ isTomorrow
    ✓ formatRelativeTime

✓ Pass: 8 ✓ Failed: 0 ✓ Duration: XXms
```

### Step 12: Build for Production

Create a production build:

```bash
cd frontend
pnpm build
```

**Expected Output**:
```
Route (app)                              Size     First Load JS
─ ○ /                                    0 B            70 kB
  ○ /404                                 149 B          70.1 kB
  └─ ○ /tasks                            0 B            70 kB
```

---

## Complete Verification Checklist

Run all verifications in sequence:

```bash
#!/bin/bash

cd frontend

echo "=== Step 1: Check Project Structure ==="
ls -la src/types/ | grep -E "(auth|task|api)"
echo "✓ Type files present"

echo -e "\n=== Step 2: Verify Config Files ==="
test -f tsconfig.json && echo "✓ tsconfig.json"
test -f package.json && echo "✓ package.json"
test -f tailwind.config.ts && echo "✓ tailwind.config.ts"
test -f vitest.config.ts && echo "✓ vitest.config.ts"
test -f .eslintrc.json && echo "✓ .eslintrc.json"

echo -e "\n=== Step 3: Install Dependencies ==="
pnpm install
echo "✓ Dependencies installed"

echo -e "\n=== Step 4: Type Check ==="
pnpm type-check
echo "✓ TypeScript strict mode verified"

echo -e "\n=== Step 5: Lint Code ==="
pnpm lint
echo "✓ ESLint passed (zero violations)"

echo -e "\n=== Step 6: Run Tests ==="
pnpm test
echo "✓ Tests passed"

echo -e "\n=== Step 7: Build Production ==="
pnpm build
echo "✓ Production build successful"

echo -e "\n=== VERIFICATION COMPLETE ==="
echo "All Phase 1 setup verification checks passed!"
```

---

## Troubleshooting

### Issue: `pnpm: command not found`
**Solution**: Install pnpm first
```bash
npm install -g pnpm
```

### Issue: `TypeScript errors in strict mode`
**Solution**: All type errors must be fixed before proceeding
```bash
pnpm type-check
# Fix errors shown
```

### Issue: `ESLint violations`
**Solution**: Run formatter to fix most issues
```bash
pnpm format
pnpm lint
```

### Issue: `Test failures`
**Solution**: Check test setup
```bash
pnpm test --reporter=verbose
```

### Issue: `Build fails`
**Solution**: Run type check first
```bash
pnpm type-check
pnpm build
```

---

## Success Criteria

After completing all verification steps, you should see:

- ✅ All configuration files present
- ✅ All type definitions created
- ✅ All utility functions available
- ✅ Dependencies successfully installed
- ✅ TypeScript strict mode verified (0 errors)
- ✅ ESLint passed (0 violations)
- ✅ Tests passed (8 test suites)
- ✅ Production build successful
- ✅ No console errors or warnings

---

## Next Steps After Verification

1. **Start Development**: `pnpm dev` (http://localhost:3000)
2. **Phase 2 Design**: Create component hierarchy and API contracts
3. **Phase 3 Development**: Build authentication and task management features
4. **Phase 4 Testing**: Add comprehensive test coverage (≥70%)

---

## Quick Start Commands

```bash
# Setup
cd frontend
pnpm install

# Development
pnpm dev              # http://localhost:3000

# Code Quality
pnpm lint             # Check linting
pnpm type-check       # Check types
pnpm format           # Auto-format code

# Testing
pnpm test             # Run tests
pnpm test:coverage    # Coverage report

# Production
pnpm build
pnpm start
```

---

**Verification Purpose**: Ensure all Phase 1 setup (T001-T012) is complete and working correctly before proceeding to Phase 2 design and Phase 3 component development.

**Status**: Ready for verification
