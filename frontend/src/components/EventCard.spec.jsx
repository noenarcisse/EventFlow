import { beforeEach, describe, expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import EventCard from "./EventCard";
import { MemoryRouter } from "react-router";

describe("Testing of the Event card component", () => {
    const mock = {
        id: 42,
        cover_color: "red",
        starts_at: new Date(),
        title: "Concert de Manau",
        city: "Bruxelles",
        venue: "Ancienne Belgique",
    };

    beforeEach(() => {
        render(
            <MemoryRouter initialEntries={["/events/42"]}>
                <EventCard ev={mock}></EventCard>
            </MemoryRouter>,
        );
    });

    test("B7_Event card is rendered in the page", () => {
        const card = screen.getByText("Concert de Manau");
        expect(card).toBeInTheDocument();
    });

    test("B8_Event card shows the correct title", () => {
        const card = screen.getByText("Concert de Manau");
        const expectedTitle = "Concert de Manau";

        expect(card).toHaveTextContent(expectedTitle);
    });
});
