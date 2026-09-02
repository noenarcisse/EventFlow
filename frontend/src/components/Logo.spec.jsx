import { describe, expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import Logo from "./Logo";

describe("Testing of the Logo component", () => {
    test("B1_Logo is loaded properly on the page", () => {
        render(<Logo></Logo>);
        const logo = screen.getByLabelText("eventflow");
        expect(logo).toBeInTheDocument();
    });

    test("B2_Logo is loaded properly on the page", () => {
        render(<Logo></Logo>);
        const logo = screen.getByLabelText("eventflow");
        expect(logo).toHaveAttribute("aria-label");
    });

    test("B3_Logo is loaded properly on the page", () => {
        render(<Logo></Logo>);
        const logo = screen.getByLabelText("eventflow");
        expect(logo).toHaveAttribute("width", "34");
    });
});
