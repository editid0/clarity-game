"use client";

import { api } from "@/convex/_generated/api";
import { useQuery } from "convex/react";
import { use, useEffect, useState } from "react";

export default function GamePage({ params }) {
    const { game_id } = use(params);
    const [userId, setUserId] = useState();
    const data = useQuery(api.myFunctions.getGameData, { game_id: game_id });
    // TODO
    // We need to get the user_id, and from that we need to check that the user is allowed to be in this game.
    useEffect(() => {
        setUserId(localStorage.getItem('user_id'))
    }, [])
    if (!data && data.length !== 1) {
        return (
            <>
                <h1 className="text-6xl font-semibold text-center">No game found.</h1>
            </>
        )
    }
    return (
        <>
            <p>{JSON.stringify(data)}</p>
        </>
    )
}