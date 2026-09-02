import { describe, expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import Avatar from "./Avatar";

describe("Testing of the Avatar component", () => {
    test("B4 Avatar shows first letters of the name", async () => {
        render(<Avatar user={{ full_name: "Camille Client" }}></Avatar>);
        const avat = await screen.findByText("CC");
        expect(avat).toBeInTheDocument();
    });

    test("B5 avat is loaded properly on the page", async () => {
        render(<Avatar user={{ email: "client@eventflow.test" }}></Avatar>);
        const avar_fallback = await screen.findByText("C");
        expect(avar_fallback).toBeInTheDocument();
    });

    test("C3 Avatar displayed size is 50px", () => {
        render(<Avatar user={{ full_name: "Jeanne Dark" }} size={50}></Avatar>);
        const avat = screen.getByText("JD");
        expect(avat).toHaveStyle("width: 50px");
        expect(avat).toHaveStyle("height: 50px");
    });

    test("C4 Avatar has 2 letters max", () => {
        render(<Avatar user={{ full_name: "Alice Bob Charlie" }}></Avatar>);
        const avat = screen.getByText("AB");
        expect(avat).toBeInTheDocument();
    });

    test("C5 Avatar is an image if there is an url", () => {
        render(<Avatar user={{ avatar: "/jarjarbinks.jpeg" }}></Avatar>);
        const avat = screen.getByRole("img");
        expect(avat).toBeInTheDocument();
        expect(avat).toHaveAttribute("src", "/jarjarbinks.jpeg");
    });
});
