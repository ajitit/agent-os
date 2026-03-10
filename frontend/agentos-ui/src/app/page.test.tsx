/**
 * File: page.test.tsx
 * 
 * Purpose:
 * Contains unit and integration tests for the root landing page (`src/app/page.tsx`).
 * 
 * Key Functionalities:
 * - Mock Next.js internal components (like `next/image`) to isolate tests
 * - Verify that critical UI elements like the main heading and chat links render correctly
 * 
 * Inputs:
 * - Rendered DOM from the `Home` component
 * 
 * Outputs:
 * - Test assertions and results
 * 
 * Interacting Files / Modules:
 * - src.app.page
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import Home from "./page";

vi.mock("next/image", () => ({
  default: (props: React.ComponentProps<"img">) => (
    // eslint-disable-next-line @next/next/no-img-element, jsx-a11y/alt-text -- mock
    <img {...props} alt={props.alt ?? ""} />
  ),
}));

describe("Home", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the main heading", () => {
    render(<Home />);
    expect(
      screen.getByRole("heading", {
        name: /enterprise multi-agent ai platform/i,
      })
    ).toBeInTheDocument();
  });

  it("renders at least one Chat link", () => {
    render(<Home />);
    const chatLinks = screen.getAllByRole("link", { name: /chat/i });
    expect(chatLinks.length).toBeGreaterThanOrEqual(1);
  });
});
