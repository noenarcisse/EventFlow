import { describe, expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import Logo from "./Logo";

describe("Testing of the Logo component", () => {
    test("B1 Logo is loaded properly on the page", () => {
        render(<Logo></Logo>);
        const logo = screen.getByLabelText("eventflow");
        expect(logo).toBeInTheDocument();
    });

    test("B2 Logo is loaded properly on the page", () => {
        render(<Logo></Logo>);
        const logo = screen.getByLabelText("eventflow");
        expect(logo).toHaveAttribute("aria-label");
    });

    test("B3 Logo is loaded properly on the page", () => {
        render(<Logo></Logo>);
        const logo = screen.getByLabelText("eventflow");
        expect(logo).toHaveAttribute("width", "34");
    });

    test("C1 Logo is size 60", () => {
        render(<Logo size={60}></Logo>);
        const logo = screen.getByLabelText("eventflow");
        expect(logo).toHaveAttribute("width", "60");
        expect(logo).toHaveAttribute("height", "60");
    });
    test("C2 Logo is size 18", () => {
        render(<Logo size={18}></Logo>);
        const logo = screen.getByLabelText("eventflow");
        expect(logo).toHaveAttribute("width", "18");
        expect(logo).toHaveAttribute("height", "18");
    });
});
