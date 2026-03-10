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
      screen.getByText("To get started, edit the page.tsx file.")
    ).toBeInTheDocument();
  });

  it("renders the Documentation link", () => {
    render(<Home />);
    expect(screen.getByRole("link", { name: /documentation/i })).toBeInTheDocument();
  });
});
