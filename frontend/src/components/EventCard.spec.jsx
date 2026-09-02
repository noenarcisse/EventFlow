import { beforeEach, describe, expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
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

    test("B7_Event card is rendered in the page", () => {
        const card = screen.getByText("Brussels Testing Days");
        expect(card).toBeInTheDocument();
    });

    test("B8_Event card appears with the right city", () => {
        const card = screen.getByText("Bruxelles");
        const expectedCity = "Bruxelles";

        expect(card).toHaveTextContent(expectedCity);
    });

    test("B9_Event card shows the proper venue", () => {
        const card = screen.getByText("Tour & Taxis");
        const expectedLocation = "Tour & Taxis";

        expect(card).toHaveTextContent(expectedLocation);
    });

    test("B10_Event card has a link", () => {
        const cards = screen.getByRole("link");
        expect(cards).toBeInTheDocument();
    });

    test("B11_Event card has the correct link", async () => {
        const cards = await screen.findByRole("link");
        expect(cards).toHaveAttribute("href", "/events/7");
    });

    test('B12_Event card has static texts "Billets" & "Voir" ', () => {
        const b = screen.getByText("Billets");
        const v = screen.getByText("Voir");

        expect(b).toBeInTheDocument();
        expect(v).toBeInTheDocument();
    });
});
