"use client";

import { api } from "@/convex/_generated/api"
import { useMutation, useQuery } from "convex/react"
import { redirect, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

export default function CreateGame() {
    const newGame = useMutation(api.myFunctions.createGame);
    const newUser = useMutation(api.myFunctions.createPlayer);
    const addToGame = useMutation(api.myFunctions.addUserToGame);
    const searchParams = useSearchParams();
    const [ready, SetReady] = useState();
    const rounds = searchParams.rounds ? searchParams.rounds : 3
    const tpr = searchParams.time_per_round ? searchParams.time_per_round : 30
    const [gameId, setGameId] = useState();
    const [userId, setUserId] = useState();

    useEffect(() => {
        SetReady(true);
        let id_ = newGame({ rounds: rounds, time_per_round: tpr })
        id_.then((e) => {
            setGameId(e);
        }
        )
    }, [])
    useEffect(() => {
        if (!localStorage.getItem('user_id')) {
            const id_ = newUser({ display_name: 'New User' })
            id_.then((e) => {
                localStorage.setItem('user_id', e)
                setUserId(e)
            })
        } else {
            setUserId(localStorage.getItem('user_id'))
        }
    }, [])
    useEffect(() => {
        if (gameId && userId) {
            addToGame({ game_id: gameId, user_id: userId, creator: true })
            redirect('/game/' + gameId)
        }
    }, [gameId, userId])
    return (
        <>
            <p>Loading...</p>
        </>
    )
}