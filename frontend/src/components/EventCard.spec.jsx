import { beforeEach, describe, expect, test } from "vitest";
import { getByText, render, screen } from "@testing-library/react";
import EventCard from "./EventCard";
import { MemoryRouter } from "react-router";

describe("Testing of the Event card component", () => {
    const mock = {
        id: 7,
        cover_color: "red",
        starts_at: new Date(),
        title: "Brussels Testing Days",
        city: "Bruxelles",
        venue: "Tour & Taxis",
    };

    beforeEach(() => {
        render(
            <MemoryRouter initialEntries={["/events/7"]}>
                <EventCard ev={mock}></EventCard>
            </MemoryRouter>,
        );
    });

    test("B7 Event card is rendered in the page", () => {
        const card = screen.getByText("Brussels Testing Days");
        expect(card).toBeInTheDocument();
    });

    test("B8 Event card appears with the right city", () => {
        const card = screen.getByText("Bruxelles");
        const expectedCity = "Bruxelles";

        expect(card).toHaveTextContent(expectedCity);
    });

    test("B9 Event card shows the proper venue", () => {
        const card = screen.getByText("Tour & Taxis");
        const expectedLocation = "Tour & Taxis";

        expect(card).toHaveTextContent(expectedLocation);
    });

    test("B10 Event card has a link", () => {
        const cards = screen.getByRole("link");
        expect(cards).toBeInTheDocument();
    });

    test("B11 Event card has the correct link", async () => {
        const cards = await screen.findByRole("link");
        expect(cards).toHaveAttribute("href", "/events/7");
    });

    test('B12 Event card has static texts "Billets" & "Voir" ', () => {
        const b = screen.getByText("Billets");
        const v = screen.getByText("Voir");

        expect(b).toBeInTheDocument();
        expect(v).toBeInTheDocument();
    });

    test('C6 Event card has a new title if modified" ', () => {
        const mock2 = {
            id: 42,
            cover_color: "red",
            starts_at: new Date(),
            title: "Namur QA Night",
            city: "Bruxelles",
            venue: "Tour & Taxis",
        };
        render(
            <MemoryRouter initialEntries={["/events/42"]}>
                <EventCard ev={mock2}></EventCard>
            </MemoryRouter>,
        );
        const card = screen.getByText("Namur QA Night");
        expect(card).toBeInTheDocument();
    });

    test('C7 Event card has a new link if id is modified" ', async () => {
        const mock2 = {
            id: 42,
            cover_color: "red",
            starts_at: new Date(),
            title: "Namur QA Night",
            city: "Bruxelles",
            venue: "Tour & Taxis",
        };
        render(
            <MemoryRouter initialEntries={["/events/42"]}>
                <EventCard ev={mock2}></EventCard>
            </MemoryRouter>,
        );

        const card = await screen.findByRole("link", {
            name: /Namur QA Night/,
        });
        expect(card).toHaveAttribute("href", "/events/42");
    });
});
